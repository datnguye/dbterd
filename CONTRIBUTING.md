# Contributing to `dbterd`

`dbterd` is open source software. It is what it is today because community members have opened issues, provided feedback, and contributed to the knowledge loop. Whether you are a seasoned open source contributor or a first-time committer, we welcome and encourage you to contribute code, documentation, ideas, or problem statements to this project.

1. [About this document](#about-this-document)
2. [Getting the code](#getting-the-code)
3. [Setting up an environment](#setting-up-an-environment)
4. [Testing dbterd](#testing)
5. [Submitting a Pull Request](#submitting-a-pull-request)

## About this document

There are many ways to contribute to the ongoing development of `dbterd`, such as by participating in discussions and issues. We encourage you to first read our higher-level document: ["Expectations for Open Source Contributors"](add-document).

The rest of this document serves as a more granular guide for contributing code changes to `dbterd` (this repository). It is not intended as a guide for using `dbterd`, and some pieces assume a level of familiarity with Python development with `poetry`. Specific code snippets in this guide assume you are using macOS or Linux and are comfortable with the command line.

### Notes

- **Adapters:** Is your issue or proposed code change related to a specific [database adapter](https://docs.getdbt.com/docs/available-adapters)? If so, please open issues, PRs, and discussions in that adapter's repository instead. The sole exception is Postgres; the `dbt-postgres` plugin lives in this repository (`dbterd`).
- **Branches:** All pull requests from community contributors should target the `main` branch (default). If the change is needed as a patch for a minor version of dbt that has already been released (or is already a release candidate), a maintainer will backport the changes in your PR to the relevant "latest" release branch (`1.0.<latest>`, `1.1.<latest>`, ...). If an issue fix applies to a release branch, that fix should be first committed to the development branch and then to the release branch (rarely release-branch fixes may not apply to `main`).
- **Releases**: Before releasing a new minor version, we prepare a series of beta release candidates to allow users to test the new version in live environments. This is an important quality assurance step, as it exposes the new code to a wide variety of complicated deployments and can surface bugs before official release. Releases are accessible via pip.

## Getting the code

### Installing git

You will need `git` in order to download and modify the `dbterd` source code. On macOS, the best way to download git is to just install [Xcode](https://developer.apple.com/support/xcode/).

### External contributors

You can contribute to `dbterd` by forking the `dbterd` repository. For a detailed overview on forking, check out the [GitHub docs on forking](https://help.github.com/en/articles/fork-a-repo). In short, you will need to:

1. Fork the `dbterd` repository
2. Clone your fork locally
3. Check out a new branch for your proposed changes
4. Push changes to your fork
5. Open a pull request against `datnguye/dbterd` from your forked repository


## Setting up an environment

There are some tools that will be helpful to you in developing locally. While this is the list relevant for `dbterd` development, many of these tools are used commonly across open-source python projects.

### Tools

We will buy `poertry` in `dbterd` development and testing.

So first install poetry via pip:
```bash
python3 -m pip install poetry --upgrade
```

then, start installing the local environment:
```bash
python3 -m poetry install
python3 -m poetry shell
pip install -e .
dbterd -h
```


## Testing

Once you're able to manually test that your code change is working as expected, it's important to run existing automated tests, as well as adding some new ones. These tests will ensure that:
- Your code changes do not unexpectedly break other established functionality
- Your code changes can handle all known edge cases
- The functionality you're adding will _keep_ working in the future

#### `pytest`

Finally, you can also run a specific test or group of tests using [`pytest`](https://docs.pytest.org/en/latest/) directly. With a virtualenv active and dev dependencies installed you can do things like:

```bash
pytest .
```

> See [pytest usage docs](https://docs.pytest.org/en/6.2.x/usage.html) for an overview of useful command-line options.

## Submitting a Pull Request

Code can be merged into the current development branch `main` by opening a pull request. A `dbterd` maintainer will review your PR. They may suggest code revision for style or clarity, or request that you add unit or integration test(s). These are good things! We believe that, with a little bit of help, anyone can contribute high-quality code.

Automated tests run via GitHub Actions. If you're a first-time contributor, all tests (including code checks and unit tests) will require a maintainer to approve. Changes in the `dbterd` repository trigger integration tests against Postgres. dbt Labs also provides CI environments in which to test changes to other adapters, triggered by PRs in those adapters' repositories, as well as periodic maintenance checks of each adapter in concert with the latest `dbterd` code changes.

Once all tests are passing and your PR has been approved, a `dbterd` maintainer will merge your changes into the active development branch. And that's it! Happy developing :tada:
