# biblion-api

This project contains the backend functionality for the biblion project, a simple pastebin-like file upload service.

## Features

- Full integration test suite
- Docker ready development environment
- Automated deployment to the container registry using GitHub Actions

## Local development

- Start a development server: `docker compose -f docker-compose.dev.yml run --service-ports app`
- Run the integration test suite: `docker compose -f docker-compose.test.yml run test`

## Deploying to production

Deployment is handled automatically using a CI pipeline every time the code is pushed.

- When the code is pushed to the `main` branch an image with the `edge` tag is deployed.
- When a semantic version git tag is pushed (e.g. `v1.2.3`) an image with the corresponding version tags is deployed (e.g. `v1` and `1.2.3`). Please make sure to honor the SemVer specification when performing a version bump (refer to [https://semver.org/]()).

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