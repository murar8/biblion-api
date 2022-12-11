# biblion-api

[![](https://github.com/murar8/biblion-api/actions/workflows/deploy.yml/badge.svg)](https://github.com/murar8/biblion-api/actions/workflows/deploy.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)

This project contains the backend functionality for the biblion project, a simple pastebin-like file upload service.

## Tech stack

|                        |                                          |
| ---------------------- | ---------------------------------------- |
| Programming Language   | [Python](https://www.python.org/)        |
| Web Framework          | [FastAPI](https://fastapi.tiangolo.com/) |
| Data Persistence Layer | [MongoDB](https://www.mongodb.com/)      |

## Features

- Full integration test suite.
- Automated quality control and deployment using GitHub Actions.
- Infrastructure as code following the [GitOps](https://www.gitops.tech/) approach.

## Local development

The easiest way to run the project locally is to open the repository inside the preconfigured development container featuring all the necessary dependencies. For more information visit [https://code.visualstudio.com/docs/devcontainers/containers](). Alternatively you will need to manually set up a MongoDB instance and a local Mailhog server to be used for development and testing.

It is recommended to run `pipenv run pre-commit-install` after cloning the repository, this will add a pre-commit check to make sure the contributed code follows the project guidelines without waiting for the CI check.

- Start a development server: `pipenv run serve`
- Run the integration test suite: `pipenv run test`

## Production infrastructure

- Database is hosted on [MongoDB Atlas](https://www.mongodb.com/atlas/database).

- SMTP service is hosted on [MailJet](https://www.mailjet.com).

- Backend infrastructure is hosted on [Google Cloud Platform](https://cloud.google.com)
  - Container images are stored on [Artifact Registry](https://cloud.google.com/artifact-registry)
  - The production environment consists of multiple instances of the application that are scaled automatically based on the load using [Cloud Run](https://cloud.google.com/run).

All the production infrastruture is managed using [Terraform](https://www.terraform.io/). Environment variables and secrets can be updated on [Terraform Cloud](https://cloud.hashicorp.com/products/terraform)

## Deployment

### Merging the code

Direct push to the `main` branch is not allowed, any updates to the production environment require a pull request to be opened.

When a PR for the `main` branch is opened or updated the following checks will run:

- Changes to the infrastructure will be validated by Terraform.
- The code will be checked for linting or formatting issues.
- The integration test suite will run.

After all checks pass the PR can be merged.

### Deployment to production

When a new git tag is pushed (e.g. `v1.2.3`):

- Changes to the infrastructure will be deployed using Terraform.

- An image with the corresponding version tags (e.g. `v1` and `1.2.3`) will be deployed to the Artifact Registry.

- The Cloud Run instance will be updated with the new image.

Please make sure to honor the SemVer specification when performing a version bump (refer to [https://semver.org/]()).

#### First deployment note

To deploy the whole infrastructure from scratch the following manual steps are necessary:

- Create a new Google Cloud Platform project
- Update the Terraform Cloud variables (`gcloud_project` and `gcloud_region`) to refer to the new project.
- Create a service account with the necessary permissions for Terraform Cloud.
- Create and export a JSON credentials key and update the Terraform Cloud variable(`GOOGLE_CREDENTIALS`) to refer to the new service account. Please note the exported key must be minified into a single line before setting it.

## License

Copyright (c) 2022 Lorenzo Murarotto <lnzmrr@gmail.com>

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
