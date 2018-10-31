if [ ! -z $TRAVIS_TAG ]; then TRAVIS_BRANCH=master; fi

CONTAINER_NAME="tkgbot-${TRAVIS_BRANCH}"
IMAGE="$DOCKER_USERNAME/$DOCKER_REPO"
source scripts/env-$TRAVIS_BRANCH.sh

restart_option=""
volume_option=""

case $TRAVIS_BRANCH in
master)
    volume_option="--volume tkgbot-data:/tkgbot/data"
    restart_option="--restart on-failure"
    ;;
develop)
    ;;
*)
    exit 1
    ;;
esac

ssh travis@$DEPLOYMENT_HOST -i scripts/id_rsa << EOF
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
    docker stop $CONTAINER_NAME
    docker image rm $IMAGE
    docker pull $IMAGE:$TRAVIS_BRANCH
    docker run -d -e "FORUM_LOGIN=$FORUM_LOGIN" \
    -e "FORUM_PASSWORD=$FORUM_PASSWORD" \
    -e "TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN" \
    $volume_option \
    $restart_option \
    --name $CONTAINER_NAME $IMAGE:$TRAVIS_BRANCH
EOF
