# Scripts vs Commands

This section introduces the various command execution features of Gameta, 
including the subtle differences between them. It comprises the following 
parts:

1. Gameta Commands
2. Gameta Scripts
3. Comparing Gameta Commands and Gameta Scripts

## Gameta Commands

Gameta Commands are a lightweight means of storing and executing simple
shell commands that do not require much customisation. They are useful for 
storing shell commands that are regularly executed and do not require the 
development of an entire script.

Gameta Commands enable users to compose, store, reuse and customise these
short CLI commands into scriptlets. This enables you to 
easily construct simple, portable scripts to manage your repositories. 

Supposing that you normally run the following commands to build and 
distribute your docker images to AWS:

```shell
# Copy relevant folders to docker folder
cp folder_a folder_b relative_path/to/dockerfile

# Build the image 
cd relative_path/to/dockerfile && docker build .

# Log in to AWS CLI
aws configure set region $AWS_REGION
aws configure set aws_accss_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY

# Log in to AWS ECR with Docker
aws ecr get-login-password | docker login --username AWS --password-stdin $AWS_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Tag and push the image the image
docker tag image_name:$IMAGE_TAG $AWS_ID.dkr.ecr.$AWS_REGION.amazonaws.com/image_name:$IMAGE_TAG
docker push $AWS_ID.dkr.ecr.$AWS_REGION.amazonaws.com/image_name:$IMAGE_TAG
```

These can be stored and execute as Gameta commands on any platform with a
similar environment setup.

```shell
# Add 1st Gameta Command to setup build
gameta cmd add \
  -n setup_build \
  -c 'cp folder_a folder_b relative_path/to/dockerfile' \
  -d "Setup folders for docker builds"

# Add 2nd Gameta Command comprising of multiple CLI commands
# to build image
gameta cmd add \
  -n build \
  -c 'cd relative_path/to/dockerfile' \
  -c 'docker build .' \
  -d "Build docker image"

# Add 3rd Gameta Command to log in to AWS
gameta cmd add \
  -n aws_login \
  -c 'aws configure set region {$AWS_REGION}' \
  -c 'aws configure set aws_accss_key_id {$AWS_ACCESS_KEY}' \
  -c 'aws configure set aws_secret_access_key {$AWS_SECRET_KEY}' \
  -d 'Login to AWS CLI'

# Add 4th Gameta Command to log in to AWS ECR
gameta cmd add \
  -n docker_login \
  -c 'aws ecr get-login-password | 
      docker login --username AWS --password-stdin {$AWS_ID}.dkr.ecr.{$AWS_REGION}.amazonaws.com' \
  -s  \  # Execute this command in a separate shell to handle the pipe token
  -d 'Login to AWS ECR'

# Add 5th Gameta Command to tag and push docker image
gameta cmd add \
  -n tag_image \
  -c 'docker tag image_name:{IMAGE_TAG} {$AWS_ID}.dkr.ecr.{$AWS_REGION}.amazonaws.com/image_name:{IMAGE_TAG}' \
  -c 'docker push {$AWS_ID}.dkr.ecr.{$AWS_REGION}.amazonaws.com/image_name:{IMAGE_TAG}' \
  -d 'Tags docker image'

# Add a Gameta Constant for the IMAGE_TAG constant
gameta const add -n IMAGE_TAG -t str -v latest

# Execute the entire pipeline
# Don't forget your environment variables 
# 1. AWS_ID
# 2. AWS_REGION
# 3. AWS_ACCESS_KEY
# 4. AWS_SECRET_KEY
AWS_ID=111111111111 \
AWS_REGION=us-west-1 \
AWS_ACCESS_KEY=XXX \
AWS_SECRET_KEY=YYY \
gameta exec -c setup_build -c build -c aws_login -c docker_login -c tag_image

# You could also add an additional command for the pipeline and execute that instead
gameta cmd add \
  -n build_distribute_pipeline \
  -c 'gameta exec -c setup_build -c build -c aws_login -c docker_login -c tag_image' \
  -d 'Build and distributes docker images to AWS ECR'

AWS_ID=111111111111 \
AWS_REGION=us-west-1 \
AWS_ACCESS_KEY=XXX \
AWS_SECRET_KEY=YYY \
gameta exec -c build_distribute_pipeline
```

See the [Applying Commands] and [Use Cases] pages for more details on how to use 
Gameta Commands.

## Gameta Scripts

Gameta Scripts enable you to create scripts with complex logic to manage your 
operations. Gameta scripts supports multiple languages i.e. you can write them
your preferred programming language (shell, Python, JavaScript, Lua...) and 
Gameta will handle the execution for you.

---
**Note**

Gameta only supports shell and Python natively. You will need to register your
preferred language separately if you wish to use it with Gameta Scripts, see
[Adding Scripting Languages] for more details.
---

You can also leverage Gameta's powerful [parameter substitution] suite to 
customise your scripts for your operations.

Supposing you have a shell script for building a docker image (as in the 
example in the previous section), and a Python script that you use for 
generating an encryption key that is copied into the image:

```shell
#!/bin/bash

# Copy relevant folders to docker folder
cp folder_a folder_b relative_path/to/dockerfile

# Build the image 
cd relative_path/to/dockerfile && docker build .

# Log in to AWS CLI
aws configure set region $AWS_REGION
aws configure set aws_accss_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY

# Log in to AWS ECR with Docker
aws ecr get-login-password | docker login --username AWS --password-stdin $AWS_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Tag and push the image the image
docker tag image_name:$IMAGE_TAG $AWS_ID.dkr.ecr.$AWS_REGION.amazonaws.com/image_name:$IMAGE_TAG
docker push $AWS_ID.dkr.ecr.$AWS_REGION.amazonaws.com/image_name:$IMAGE_TAG
```

```python
#!/usr/bin/env python3

from cryptography.fernet import Fernet
key = Fernet.generate_key()
with open("relative_path/to/dockerfile/{{ ENCRYPTION_FILE_NAME }}", "wb") as f:
    f.write(key)
```

These existing scripts can be imported with the following commands:

```shell
# Register the shell script
gameta scripts register \
  -n build_script \         # Name of the script
  -c linux.build  \         # Category of the script
  -d "Builds on Linux" \    # A brief description of the script
  -l shell \                # Language that the script is written in
  -p current/path/to/script # Path where the script is currently stored

# Register the Python script
gameta scripts register \
  -n generate_key \
  -c linux.build \
  -d "Generate key in Linux" \  
  -l python \
  -p current/path/to/script2
```

The scripts are then stored under the `.gameta/scripts` folder:

```
.gameta
|--> .gameta  # File for storing Gameta configuration
|--> scripts  # Folder for storing Gameta scripts
     |--> linux
          |--> build
               |--> build_script.sh
               |--> generate_key.py
|--> configs  # Folder for storing user-defined configurations
```

To execute these scripts, run the following command:

```shell
# Execute the Gameta scripts
AWS_ID=111111111111 \
AWS_REGION=us-west-1 \
AWS_ACCESS_KEY=XXX \
AWS_SECRET_KEY=YYY \
gameta exec generate_key build_script
```

See the [Executing Scripts] and [Use Cases] pages for more details on how to use Gameta Scripts.

## Comparing Gameta Commands vs Gameta Scripts

The table below summarises the differences between Gameta Commands and Gameta Scripts:

| Aspect        | Gameta Commands | Gameta Scripts  |
| ------------- | ----------------- | --------------- |
| Purpose       | Simple shell commands | Complex programmes |
| Parameter Substitution | <ul><li>Repository Parameters</li><li>Gameta Constants</li><li>Environment Variables</li></ul> | <ul><li>Repository Parameters</li><li>Gameta Constants</li><li>Environment Variables</li><li>Bash Commands</li><li>Or logic</li></ul>
| Substitution Format | Single curly braces "{ }" | Double curly braces "{{ }}" |
| Execution | `gameta exec -c cmd` | `gameta exec script` |  
| Storage | Inside `.gameta` JSON file | Under `.gameta/scripts` |


[Applying Commands]: applying_commands.md
[Use Cases]: ../applications/use_cases.md
[Adding Scripting Languages]: ../customisation/adding_scripting_languages.md
[parameter substitution]: executing_scripts.md
[Executing Scripts]: executing_scripts.md