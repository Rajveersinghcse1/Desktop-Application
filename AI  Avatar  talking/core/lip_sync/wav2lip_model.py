"""
Wav2Lip Model Architecture
PyTorch implementation of Wav2Lip model
"""

import torch
from torch import nn


class Conv2d(nn.Module):
    """2D Convolution block with BatchNorm"""
    
    def __init__(self, cin, cout, kernel_size, stride, padding, residual=False):
        super().__init__()
        self.conv_block = nn.Sequential(
            nn.Conv2d(cin, cout, kernel_size, stride, padding),
            nn.BatchNorm2d(cout)
        )
        self.act = nn.ReLU()
        self.residual = residual
    
    def forward(self, x):
        out = self.conv_block(x)
        if self.residual:
            out += x
        return self.act(out)


class Wav2Lip(nn.Module):
    """Wav2Lip model for lip synchronization"""
    
    def __init__(self):
        super(Wav2Lip, self).__init__()
        
        # Face encoder
        self.face_encoder_blocks = nn.ModuleList([
            nn.Sequential(
                Conv2d(6, 16, kernel_size=7, stride=1, padding=3)
            ),  # 96x96
            
            nn.Sequential(
                Conv2d(16, 32, kernel_size=3, stride=2, padding=1),  # 48x48
                Conv2d(32, 32, kernel_size=3, stride=1, padding=1, residual=True),
                Conv2d(32, 32, kernel_size=3, stride=1, padding=1, residual=True)
            ),
            
            nn.Sequential(
                Conv2d(32, 64, kernel_size=3, stride=2, padding=1),  # 24x24
                Conv2d(64, 64, kernel_size=3, stride=1, padding=1, residual=True),
                Conv2d(64, 64, kernel_size=3, stride=1, padding=1, residual=True),
                Conv2d(64, 64, kernel_size=3, stride=1, padding=1, residual=True)
            ),
            
            nn.Sequential(
                Conv2d(64, 128, kernel_size=3, stride=2, padding=1),  # 12x12
                Conv2d(128, 128, kernel_size=3, stride=1, padding=1, residual=True),
                Conv2d(128, 128, kernel_size=3, stride=1, padding=1, residual=True)
            ),
            
            nn.Sequential(
                Conv2d(128, 256, kernel_size=3, stride=2, padding=1),  # 6x6
                Conv2d(256, 256, kernel_size=3, stride=1, padding=1, residual=True),
                Conv2d(256, 256, kernel_size=3, stride=1, padding=1, residual=True)
            ),
            
            nn.Sequential(
                Conv2d(256, 512, kernel_size=3, stride=2, padding=1),  # 3x3
                Conv2d(512, 512, kernel_size=3, stride=1, padding=1, residual=True)
            ),
            
            nn.Sequential(
                Conv2d(512, 512, kernel_size=3, stride=1, padding=0),  # 1x1
                Conv2d(512, 512, kernel_size=1, stride=1, padding=0)
            )
        ])
        
        # Audio encoder
        self.audio_encoder = nn.Sequential(
            Conv2d(1, 32, kernel_size=3, stride=1, padding=1),
            Conv2d(32, 32, kernel_size=3, stride=1, padding=1, residual=True),
            Conv2d(32, 32, kernel_size=3, stride=1, padding=1, residual=True),
            
            Conv2d(32, 64, kernel_size=3, stride=(3, 1), padding=1),
            Conv2d(64, 64, kernel_size=3, stride=1, padding=1, residual=True),
            Conv2d(64, 64, kernel_size=3, stride=1, padding=1, residual=True),
            
            Conv2d(64, 128, kernel_size=3, stride=3, padding=1),
            Conv2d(128, 128, kernel_size=3, stride=1, padding=1, residual=True),
            Conv2d(128, 128, kernel_size=3, stride=1, padding=1, residual=True),
            
            Conv2d(128, 256, kernel_size=3, stride=(3, 2), padding=1),
            Conv2d(256, 256, kernel_size=3, stride=1, padding=1, residual=True),
            
            Conv2d(256, 512, kernel_size=3, stride=1, padding=0),
            Conv2d(512, 512, kernel_size=1, stride=1, padding=0)
        )
        
        # Face decoder
        self.face_decoder_blocks = nn.ModuleList([
            nn.Sequential(
                Conv2d(512, 512, kernel_size=1, stride=1, padding=0)
            ),
            
            nn.Sequential(
                nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),
                Conv2d(1024, 512, kernel_size=3, stride=1, padding=1, residual=True)
            ),  # 3x3
            
            nn.Sequential(
                nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),
                Conv2d(1024, 512, kernel_size=3, stride=1, padding=1, residual=True),
                Conv2d(512, 512, kernel_size=3, stride=1, padding=1, residual=True)
            ),  # 6x6
            
            nn.Sequential(
                nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),
                Conv2d(768, 384, kernel_size=3, stride=1, padding=1),
                Conv2d(384, 384, kernel_size=3, stride=1, padding=1, residual=True),
                Conv2d(384, 384, kernel_size=3, stride=1, padding=1, residual=True)
            ),  # 12x12
            
            nn.Sequential(
                nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),
                Conv2d(512, 256, kernel_size=3, stride=1, padding=1),
                Conv2d(256, 256, kernel_size=3, stride=1, padding=1, residual=True),
                Conv2d(256, 256, kernel_size=3, stride=1, padding=1, residual=True)
            ),  # 24x24
            
            nn.Sequential(
                nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),
                Conv2d(320, 128, kernel_size=3, stride=1, padding=1),
                Conv2d(128, 128, kernel_size=3, stride=1, padding=1, residual=True),
                Conv2d(128, 128, kernel_size=3, stride=1, padding=1, residual=True)
            ),  # 48x48
            
            nn.Sequential(
                nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),
                Conv2d(160, 64, kernel_size=3, stride=1, padding=1),
                Conv2d(64, 64, kernel_size=3, stride=1, padding=1, residual=True),
                Conv2d(64, 64, kernel_size=3, stride=1, padding=1, residual=True)
            )  # 96x96
        ])
        
        # Output layer
        self.output_block = nn.Sequential(
            Conv2d(80, 32, kernel_size=3, stride=1, padding=1),
            nn.Conv2d(32, 3, kernel_size=1, stride=1, padding=0),
            nn.Sigmoid()
        )
    
    def forward(self, audio_sequences, face_sequences):
        """
        Forward pass
        
        Args:
            audio_sequences: (B, T, 1, 80, 16) mel spectrogram
            face_sequences: (B, T, 6, H, W) face sequences
        
        Returns:
            Generated face with lip movements
        """
        B = audio_sequences.size(0)
        
        input_dim_size = len(face_sequences.size())
        if input_dim_size > 4:
            audio_sequences = torch.cat([audio_sequences[:, i] for i in range(audio_sequences.size(1))], dim=0)
            face_sequences = torch.cat([face_sequences[:, :, i] for i in range(face_sequences.size(2))], dim=0)
        
        # Audio encoding
        audio_embedding = self.audio_encoder(audio_sequences)  # B, 512, 1, 1
        
        # Face encoding
        feats = []
        x = face_sequences
        for f in self.face_encoder_blocks:
            x = f(x)
            feats.append(x)
        
        # Face decoding with audio conditioning
        x = audio_embedding
        for f in self.face_decoder_blocks:
            x = f(x)
            try:
                x = torch.cat((x, feats[-1]), dim=1)
            except Exception:
                pass
            feats.pop()
        
        x = self.output_block(x)
        
        if input_dim_size > 4:
            x = torch.split(x, B, dim=0)  # [(B, C, H, W)]
            outputs = torch.stack(x, dim=2)  # (B, C, T, H, W)
        else:
            outputs = x
        
        return outputs


if __name__ == '__main__':
    # Test model
    model = Wav2Lip()
    print("Wav2Lip model created")
    print(f"Total parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Test forward pass
    audio = torch.randn(1, 1, 80, 16)
    face = torch.randn(1, 6, 96, 96)
    
    with torch.no_grad():
        output = model(audio, face)
    
    print(f"Output shape: {output.shape}")
