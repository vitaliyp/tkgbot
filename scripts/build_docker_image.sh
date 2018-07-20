echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker pull $DOCKER_USERNAME/$DOCKER_REPO
docker build . -t $DOCKER_USERNAME/$DOCKER_REPO:$TRAVIS_COMMIT -t $DOCKER_USERNAME/$DOCKER_REPO
docker push $DOCKER_USERNAME/$DOCKER_REPO
