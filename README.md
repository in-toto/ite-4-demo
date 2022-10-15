# ITE-4-demo

A simple demo that shows some of the capabilities that ITE-4 enables.


## Demo setup

Clone this repository recursively. It includes a monkey-patched version of
in-toto. Install this version of in-toto to your machine.

```shell
git clone --recursive https://github.com/in-toto/ite-4-demo.git
cd ite-4-demo/in-toto
pip install .

# Go back to the demo's home directory.
cd ..
```

For this demo, make sure you have the [github cli tool](https://cli.github.com/)
installed.


## Run the demo commands

### 1. Clone project source code (Bob & Alice)

Since we don't have the project installed locally, we will be cloning them 
ourselves. But in the real world, it is more likely that Bob and Alice already
have the project locally.

**Note:** If you are testing this demo locally, use a personal fork of the
`ite-4-demo-test-repo` since you will need access to make and merge PR's. So
replace the repo link below with one pointing to your fork.

```shell
git clone https://github.com/in-toto/ite-4-demo-test-repo.git functionary_bob/ite-4-demo-test-repo
git clone https://github.com/in-toto/ite-4-demo-test-repo.git owner_alice/ite-4-demo-test-repo
```

### 2. Define the software supply chain layout (Alice)

```shell
cd owner_alice
python create_layout.py
```

### 3. Update version number (Bob)

Before Bob makes any changes, he will first create a `feature` branch that will
contain his changes.

```shell
cd ../functionary_bob/ite-4-demo-test-repo
git checkout -b feature
```

Bob uses `in-toot-record` command to record the state of the files he will
modify. The material will be latest merge-commit.

```shell
# We use a generic uri to represent a Github entity
# A github commit looks like: github:org/repo:commit:id

in-toto-record start --step-name update-version --key ../bob -m github:in-toto/ite-4-demo-test-repo:commit:{previously merged commit id}
```

Then, Bob uses an editor of his choice to update the version number in `foo.py`

```shell
# Change version number from v0 to v1
sed -i.bak 's/v0/v1/' foo.py && rm foo.py.bak
```

Finally, Bob records the state of the files after the modification and produces
a link metadata file called `update-version.[Bob's keyid].link`.

```
in-toto-record stop --step-name update-version --key ../bob -p foo.py
```

### 4. Submit a pull request (Bob)

Bob has done his work and will commit and push the changes to the remote repo.

```shell
git add foo.py
git commit -m "update version"
git push --set-upstream origin feature
```

Then, Bob will submit a pull request using `gh` and use `in-toto-run` to
record the state of the files to create a link.

```shell
gh pr create --title "Update version" --body "Update version number"
in-toto-run -n pull-request -m  . -p github:in-toto/ite-4-demo-test-repo:pr:{pr number} --key ../bob --no-command
```

### 5. Approve and merge PR (Alice)

Alice will now review Bob's PR, approve it, and merged it.

```shell
cd ../../owner_alice/ite-4-demo-test-repo
gh pr merge {pr number}
in-toto-run -n merge-pr -m . -p . --key ../alice --no-command
```

### 6. Create a tag (Alice)

Then, Alice will tag the new merge commit and record the action.

```shell
in-toto-run -n tag -m . -p . --key ../alice -- git tag v0.1
```

### 7. Build the Container Image locally (Alice)

Alice can now build the container image.

```shell
docker build . --tag ite-4-demo
```
