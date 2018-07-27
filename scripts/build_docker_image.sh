IMAGE="$DOCKER_USERNAME/$DOCKER_REPO"

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker pull $IMAGE:$TRAVIS_BRACH
docker build . -t $IMAGE:$TRAVIS_COMMIT -t $IMAGE:$TRAVIS_BRANCH -t $IMAGE
docker push $IMAGE
