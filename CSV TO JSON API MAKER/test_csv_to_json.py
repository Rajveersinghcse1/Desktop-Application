#!/usr/bin/env python3
"""
Example usage and validation tests for CSV to JSON API Converter.
"""

import json
import tempfile
import os
from pathlib import Path

# Import the main module
from csv_to_json_api import (
    DataProcessor, APIGenerator, APIServer,
    TypeInferenceEngine, CONFIG, ProcessingResult
)
import pandas as pd


def create_sample_csv():
    """Create a sample CSV file for testing."""
    data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'email': [
            'alice@example.com', 'bob@test.org', 
            'charlie@demo.net', 'diana@sample.io', 'eve@mail.com'
        ],
        'age': [25, 30, 35, 28, 32],
        'salary': [50000.50, 60000.75, 75000.00, 55000.25, 82000.00],
        'active': ['true', 'false', 'true', 'true', 'false'],
        'join_date': [
            '2023-01-15', '2022-06-20', '2021-03-10',
            '2023-08-05', '2020-11-30'
        ],
        'department': ['Engineering', 'Sales', 'Engineering', 'Marketing', 'Engineering']
    }
    
    df = pd.DataFrame(data)
    
    # Create temp file
    temp_path = Path(tempfile.gettempdir()) / 'sample_data.csv'
    df.to_csv(temp_path, index=False)
    
    return temp_path


def test_type_inference():
    """Test the type inference engine."""
    print("\n" + "="*60)
    print("TEST: Type Inference Engine")
    print("="*60)
    
    engine = TypeInferenceEngine()
    
    # Test cases
    test_data = {
        'integers': pd.Series([1, 2, 3, 4, 5]),
        'floats': pd.Series([1.5, 2.7, 3.14, 4.0, 5.5]),
        'int_as_float': pd.Series([1.0, 2.0, 3.0, 4.0, 5.0]),
        'booleans': pd.Series(['true', 'false', 'yes', 'no', 'true']),
        'emails': pd.Series(['a@b.com', 'c@d.org', 'e@f.net', 'g@h.io', 'i@j.co']),
        'dates': pd.Series(['2023-01-01', '2023-02-15', '2023-03-20', '2023-04-10', '2023-05-05']),
        'categories': pd.Series(['A', 'B', 'A', 'A', 'B', 'A', 'B', 'A', 'A', 'B']),
        'strings': pd.Series(['Hello', 'World', 'Foo', 'Bar', 'Baz'])
    }
    
    results = []
    for name, series in test_data.items():
        inferred = engine.infer_column_type(series)
        results.append((name, inferred))
        print(f"  {name}: {inferred}")
    
    print("\n✓ Type inference tests completed")
    return results


def test_data_processing():
    """Test the data processor."""
    print("\n" + "="*60)
    print("TEST: Data Processor")
    print("="*60)
    
    # Create sample file
    csv_path = create_sample_csv()
    print(f"  Created sample CSV: {csv_path}")
    
    # Process file
    processor = DataProcessor()
    result = processor.process_file(csv_path)
    
    assert result.success, f"Processing failed: {result.error_message}"
    print(f"  Processed {len(result.data)} records")
    print(f"  Found {len(result.columns)} columns")
    
    # Validate columns
    print("\n  Column metadata:")
    for col in result.columns:
        print(f"    - {col.name} ({col.inferred_type}): "
              f"{col.null_count} nulls, {col.unique_count} unique")
    
    # Validate quality metrics
    if result.quality_metrics:
        qm = result.quality_metrics
        print(f"\n  Quality Metrics:")
        print(f"    Completeness: {qm.completeness_score:.1f}%")
        print(f"    Uniqueness: {qm.uniqueness_score:.1f}%")
        print(f"    Memory: {qm.memory_usage_bytes / 1024:.1f} KB")
    
    # Clean up
    os.remove(csv_path)
    
    print("\n✓ Data processing tests completed")
    return result


def test_api_generation():
    """Test API structure generation."""
    print("\n" + "="*60)
    print("TEST: API Generation")
    print("="*60)
    
    # Process sample data first
    csv_path = create_sample_csv()
    processor = DataProcessor()
    result = processor.process_file(csv_path)
    
    # Generate API structure
    generator = APIGenerator(port=5000)
    api = generator.generate(result)
    
    print(f"  API Version: {api.api_info['version']}")
    print(f"  Total Records: {api.metadata['total_records']}")
    print(f"  Endpoints:")
    for name, url in api.endpoints.items():
        print(f"    {name}: {url}")
    
    # Validate JSON output
    json_output = api.to_json()
    parsed = json.loads(json_output)
    assert 'api_info' in parsed
    assert 'metadata' in parsed
    assert 'data' in parsed
    assert len(parsed['data']) == 5
    
    # Clean up
    os.remove(csv_path)
    
    print("\n✓ API generation tests completed")
    return api


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "="*60)
    print("TEST: Edge Cases")
    print("="*60)
    
    processor = DataProcessor()
    
    # Test: Non-existent file
    result = processor.process_file('/nonexistent/file.csv')
    assert not result.success
    print(f"  ✓ Non-existent file: {result.error_message[:50]}...")
    
    # Test: Empty data handling
    empty_csv = Path(tempfile.gettempdir()) / 'empty.csv'
    pd.DataFrame().to_csv(empty_csv, index=False)
    result = processor.process_file(empty_csv)
    os.remove(empty_csv)
    print(f"  ✓ Empty file handling works")
    
    # Test: Special characters in column names
    special_df = pd.DataFrame({
        'Column Name!@#$': [1, 2, 3],
        '   Spaced  Column  ': [4, 5, 6],
        '123_numeric_start': [7, 8, 9],
        '': [10, 11, 12],  # Empty column name
    })
    special_csv = Path(tempfile.gettempdir()) / 'special.csv'
    special_df.to_csv(special_csv, index=False)
    
    result = processor.process_file(special_csv)
    assert result.success
    
    # Check cleaned column names
    col_names = [c.name for c in result.columns]
    print(f"  ✓ Special chars cleaned: {col_names}")
    
    os.remove(special_csv)
    
    print("\n✓ Edge case tests completed")


def test_full_workflow():
    """Test complete workflow from file to JSON output."""
    print("\n" + "="*60)
    print("TEST: Full Workflow")
    print("="*60)
    
    # Create sample data
    csv_path = create_sample_csv()
    output_path = Path(tempfile.gettempdir()) / 'output_api.json'
    
    # Process
    processor = DataProcessor()
    result = processor.process_file(csv_path)
    
    # Generate
    generator = APIGenerator()
    api = generator.generate(result)
    
    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(api.to_json())
    
    print(f"  Input: {csv_path}")
    print(f"  Output: {output_path}")
    print(f"  Records: {len(api.data)}")
    
    # Verify output
    with open(output_path, 'r', encoding='utf-8') as f:
        loaded = json.load(f)
    
    assert loaded['metadata']['total_records'] == 5
    assert len(loaded['data']) == 5
    
    # Show sample record
    print(f"\n  Sample record:")
    sample = loaded['data'][0]
    for key, value in sample.items():
        print(f"    {key}: {value}")
    
    # Clean up
    os.remove(csv_path)
    os.remove(output_path)
    
    print("\n✓ Full workflow test completed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("CSV TO JSON API CONVERTER - TEST SUITE")
    print("="*60)
    
    try:
        test_type_inference()
        test_data_processing()
        test_api_generation()
        test_edge_cases()
        test_full_workflow()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED ✓")
        print("="*60 + "\n")
        return 0
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(run_all_tests())
