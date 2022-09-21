mkdir tmp
cd tmp

docker run --rm repronim/neurodocker:0.7.0 generate docker \
  --pkg-manager apt \
  --base debian:buster-slim \
  --fsl version=6.0.3 \
  --miniconda \
       version=py37_4.10.3 \
       create_env=neuro \
       pip_install="setuptools==65.3.0 Cython==0.29.32 nibabel==4.0.2 nilearn==0.9.2 nipype==1.8.4 numpy==1.21.6 pandas==1.3.5 scikit-learn==1.0.2 scipy==1.7.3" \
       activate=true \
> fsl603.Dockerfile

docker build --tag zenkavi/fsl:6.0.3 --file fsl603.Dockerfile .
