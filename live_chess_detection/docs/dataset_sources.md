# Dataset Sources

This document describes the multi-source dataset used for training the chess vision system.

## Dataset Composition

| Source | Images | Percentage | License | Quality |
|--------|--------|------------|---------|---------|
| Synthetic | 15,000 | 35% | N/A (Generated) | High |
| Roboflow | 8,000 | 30% | CC BY 4.0 | Medium |
| Kaggle | 6,000 | 25% | CC0/Public Domain | Medium |
| YouTube | 3,000 | 10% | Fair Use | Low |

**Total**: 32,000 images

## Source Details

### 1. Synthetic Dataset (35%)

**Source**: Generated from Chess.com games
**Images**: 15,000
**Quality**: High
**License**: N/A (Generated)

#### Generation Process

1. **Game Extraction**: Extract positions from Chess.com games
2. **Board Rendering**: Generate board images with various styles
3. **Piece Placement**: Place pieces using computer graphics
4. **Augmentation**: Apply lighting, shadows, and textures

#### Advantages

- Perfect annotations
- Consistent quality
- Diverse board styles
- Scalable generation

#### Challenges

- May not reflect real-world conditions
- Limited texture variation
- Perfect lighting conditions

### 2. Roboflow Dataset (30%)

**Source**: Roboflow Universe
**Images**: 8,000
**Quality**: Medium
**License**: CC BY 4.0

#### Collection Process

1. **Data Scraping**: Collect from Roboflow Universe
2. **Quality Filtering**: Remove low-quality images
3. **Annotation Review**: Verify piece annotations
4. **Format Standardization**: Convert to YOLO format

#### Advantages

- Real-world images
- Diverse lighting conditions
- Various board materials
- Professional annotations

#### Challenges

- Inconsistent quality
- Limited board styles
- Annotation errors

### 3. Kaggle Dataset (25%)

**Source**: Kaggle competitions and datasets
**Images**: 6,000
**Quality**: Medium
**License**: CC0/Public Domain

#### Collection Sources

- Chess.com dataset
- Lichess dataset
- Tournament photos
- Educational materials

#### Advantages

- Public domain
- Diverse sources
- Good variety
- Easy access

#### Challenges

- Mixed quality
- Inconsistent annotations
- Copyright concerns

### 4. YouTube Dataset (10%)

**Source**: Tournament footage
**Images**: 3,000
**Quality**: Low
**License**: Fair Use

#### Extraction Process

1. **Video Download**: Download tournament videos
2. **Frame Extraction**: Extract key frames
3. **Manual Annotation**: Annotate pieces manually
4. **Quality Control**: Filter for usable images

#### Advantages

- Real tournament conditions
- Dynamic lighting
- Professional setups
- Authentic scenarios

#### Challenges

- Low resolution
- Motion blur
- Annotation difficulty
- Copyright issues

## Data Preprocessing

### 1. Image Standardization

```python
# Resize to standard resolution
image = cv2.resize(image, (1024, 1024))

# Normalize pixel values
image = image.astype(np.float32) / 255.0
```

### 2. Annotation Format

```yaml
# YOLO format
class_id center_x center_y width height
0 0.5 0.5 0.1 0.1
```

### 3. Quality Control

- Remove blurry images
- Filter low-resolution images
- Verify annotation accuracy
- Check for duplicates

## Augmentation Strategy

### 1. Geometric Augmentations

- Rotation: ±15 degrees
- Translation: ±10%
- Scale: 0.8-1.2
- Flip: Horizontal only

### 2. Photometric Augmentations

- Brightness: ±20%
- Contrast: ±20%
- Saturation: ±20%
- Hue: ±10%

### 3. Domain-Specific Augmentations

- Board style variation
- Lighting conditions
- Shadow effects
- Piece material changes

## Dataset Splits

| Split | Images | Percentage | Purpose |
|-------|--------|------------|---------|
| Train | 25,600 | 80% | Model training |
| Validation | 3,200 | 10% | Hyperparameter tuning |
| Test | 3,200 | 10% | Final evaluation |

## Quality Metrics

### 1. Annotation Quality

- **Accuracy**: 95%+ annotation accuracy
- **Consistency**: Standardized format
- **Completeness**: All pieces annotated

### 2. Image Quality

- **Resolution**: Minimum 512x512
- **Sharpness**: No motion blur
- **Lighting**: Adequate illumination
- **Contrast**: Clear piece boundaries

### 3. Diversity Metrics

- **Board Styles**: 15+ different styles
- **Lighting**: 10+ lighting conditions
- **Angles**: Multiple viewing angles
- **Materials**: Various board materials

## Usage Guidelines

### 1. Training

```python
# Load dataset
dataset = ChessDataset(
    data_dir='data/chess_dataset',
    split='train',
    augment=True
)
```

### 2. Validation

```python
# Load validation set
val_dataset = ChessDataset(
    data_dir='data/chess_dataset',
    split='validation',
    augment=False
)
```

### 3. Testing

```python
# Load test set
test_dataset = ChessDataset(
    data_dir='data/chess_dataset',
    split='test',
    augment=False
)
```

## Future Improvements

### 1. Data Collection

- More tournament footage
- Diverse board styles
- Better lighting conditions
- Higher resolution images

### 2. Annotation Quality

- Professional annotators
- Multiple annotators per image
- Consensus-based annotations
- Quality control metrics

### 3. Dataset Expansion

- Real-time game footage
- Mobile device captures
- Different chess variants
- 3D board representations

## References

- [Roboflow Universe](https://universe.roboflow.com/)
- [Kaggle Datasets](https://www.kaggle.com/datasets)
- [Chess.com API](https://www.chess.com/news/view/published-data-api)
- [Lichess API](https://lichess.org/api)
