pipeline {
    agent {
        node {
            label 'linux && docker'
            customWorkspace "workspace/${env.JOB_NAME}/${env.BUILD_NUMBER}"
        }
    }

    parameters {
        string(
            name: 'DOCKER_REGISTRY',
            defaultValue: '',
            description: 'URL of the Docker Registry'
        )
        string(
            name: 'DOCKER_NAMESPACE',
            defaultValue: 'aprelius',
            description: 'Docker namespace to create the containers in'
        )
        string(
            name: 'DOCKER_CONTAINER',
            defaultValue: 'tplink-monitor',
            description: 'Name of the container'
        )
        booleanParam(
            name: 'LATEST_TAG',
            defaultValue: true,
            description: 'Push the new latest tag'
        )
    }

    environment {
        GIT_SHORT_COMMIT = sh(
            returnStdout: true,
            script: "git log -n 1 --pretty=format:'%h'").trim()
    }

    stages {
        stage('Validate parameters') {
            steps {
                script {
                    sh "/bin/true"
                }
            }
        }
        stage('Build Container') {
            steps {
                script {
                    sh """
                    docker build \
                        --force-rm \
                        --no-cache \
                        --network=host \
                        -f Dockerfile \
                        -t ${params.DOCKER_REGISTRY}/${params.DOCKER_NAMESPACE}/${params.DOCKER_CONTAINER}:${GIT_SHORT_COMMIT} \
                        -t ${params.DOCKER_REGISTRY}/${params.DOCKER_NAMESPACE}/${params.DOCKER_CONTAINER}:latest \
                        .
                    """
                }
            }
        }
        stage('Test Container') {
            steps {
                sh "/bin/true"
            }
        }
        stage('Publish Agent') {
            steps {
                script {
                    sh "docker push ${params.DOCKER_REGISTRY}/${params.DOCKER_NAMESPACE}/${params.DOCKER_CONTAINER}:${GIT_SHORT_COMMIT}"
                    if (env.LATEST_TAG.toBoolean()) {
                        sh "docker push ${params.DOCKER_REGISTRY}/${params.DOCKER_NAMESPACE}/${params.DOCKER_CONTAINER}:latest"
                    }
                }
            }
        }
    }

    post {
        always {
            sh """
            docker rmi \
                ${params.DOCKER_REGISTRY}/${params.DOCKER_NAMESPACE}/${params.DOCKER_CONTAINER}:${GIT_SHORT_COMMIT} \
                ${params.DOCKER_REGISTRY}/${params.DOCKER_NAMESPACE}/${params.DOCKER_CONTAINER}:latest
            """
        }
    }
}
