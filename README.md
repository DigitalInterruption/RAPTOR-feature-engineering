# Containerised feature engineering pipeline
This is the repo the feature-engineering images will be built from, migrated from micro-raptor repo, see [dockerBuild tag](https://github.com/DigitalInterruption/Micro-RAPTOR/releases/tag/dockerBuild) for original testing and refactoring.

## Modes
Currently there are two modes of this pipeline, batch and family, both process a full dataset into either a family feature map or a feature map for each individual sample. These versions are tagged as such to denote the difference in the produced feature map.
