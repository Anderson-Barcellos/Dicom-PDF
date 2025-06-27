- name: Build Docker image
  run: docker build . --tag my-image-name:$(date +%s)
