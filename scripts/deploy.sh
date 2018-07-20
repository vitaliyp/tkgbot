CONTAINER_NAME=tkgbot-staging

ssh travis@$DEPLOYMENT_HOST -i scripts/id_rsa << EOF
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
    docker stop $CONTAINER_NAME
    docker image rm $DOCKER_USERNAME/$DOCKER_REPO
    docker pull $DOCKER_USERNAME/$DOCKER_REPO
    docker run -d -e FORUM_LOGIN=$FORUM_LOGIN -e FORUM_PASSWORD=$FORUM_PASSWORD -e TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN --rm --name $CONTAINER_NAME $DOCKER_USERNAME/$DOCKER_REPO
EOF
