mkdir tmp
cd tmp

docker run --rm repronim/neurodocker:0.7.0 generate docker \
  --pkg-manager apt \
  --base debian:buster-slim \
  --fsl version=6.0.3 \
  --miniconda \
       version=py37_4.10.3 \
       create_env=neuro \
       pip_install="setuptools Cython nibabel nilearn nipype numpy pandas scipy" \
       activate=true \
> fsl603.Dockerfile

docker build --tag fsl:6.0.3 --file fsl603.Dockerfile .
