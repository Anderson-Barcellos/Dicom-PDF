- name: Build Docker image
  run: docker build . --file caminho/para/Dockerfile --tag my-image-name:$(date +%s)
