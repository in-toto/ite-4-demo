# ITE-4-demo

A simple demo that shows some of the capabilities that ITE-4 enables.


## Demo setup

Clone this repository recursively and set up a virtual environment to contain
all the dependencies for the demo.

```shell
git clone --recursive git@github.com:in-toto/ite-4-demo.git && cd ite-4-demo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

This repo includes a monkey-patched version of in-toto. Install it on your 
machine machine.

```shell
cd in-toto
pip install .

# Go back to the demo's home directory.
cd ..
```

For this demo, make sure you have the [github cli tool](https://cli.github.com/)
installed.

Also, clone test projects into the home directories of the "players" involved,
Alice and Bob. In the real world, it is more likely that both already have the
project installed locally.

**Note:** If you are testing this demo locally, use a personal fork of the
`ite-4-demo-test-repo` since you will need access to make and merge PR's. So
replace the repo link below with one pointing to your fork.

```shell
git clone git@github.com:in-toto/ite-4-demo-test-repo.git functionary_bob/project
git clone git@github.com:in-toto/ite-4-demo-test-repo.git owner_alice/project
```

## Run the demo commands

### 1. Define the software supply chain layout (Alice)

```shell
cd owner_alice
python create_layout.py
```

### 2. Make and commit changes to the project (Bob)

Before Bob makes any changes, he will first create a `feature` branch that will
contain his changes.

```shell
cd ../functionary_bob/project
git checkout -b feature
```

Bob uses `in-toot-record` command to record the change in the commit hash. The
material will be the latest commit on HEAD.

```shell
in-toto-record start --step-name commit-changes --key ../bob -m git:commit
```

Then, Bob uses an editor of his choice to update the version number in `foo.py`
and commits the changes to the branch.

```shell
# Change version number from v0 to v1
sed -i.bak 's/v0/v1/' foo.py && rm foo.py.bak
git add foo.py && git commit -m "update version"
```

Finally, Bob records the state of the files after the modification and produces
a link metadata file called `update-version.[Bob's keyid].link`.

```
in-toto-record stop --step-name commit-changes --key ../bob -p git:commit
```

### 3. Create a pull request (Bob)

Now that Bob has commited his changes to his local repo, he will push the
changes to the remote repo.

```shell
git push --set-upstream origin feature
```

Then, Bob will submit a pull request using `gh` and use `in-toto-run` to
record the state of the files to create a link. The output of the `gh` command
should give you the pull request number, replace the placeholders in the
following commands with it.

```shell
in-toto-record start -n create-pr -m git:commit --key ../bob
gh pr create --title "update version" --body "update version number"
in-toto-record stop -n create-pr -p github:in-toto/ite-4-demo-test-repo:pr:{pr number} --key ../bob
```

### 4. Approve and merge PR (Alice)

Alice will now review Bob's PR, approve it, and merge it. In order to record the
merging, Alice will need to pull the new merge commit and record it.

```shell
cd ../../owner_alice/project
in-toto-record start -n merge-pr -m github:in-toto/ite-4-demo-test-repo:pr:{pr number} git:commit --key ../alice
gh pr merge {pr number}
git pull
in-toto-record stop -n merge-pr -p git:commit --key ../alice
```

### 5. Create a tag (Alice)

Then, Alice will tag the new merge commit and record the action.

```shell
in-toto-run -n tag -m git:commit -p git:tag:release --key ../alice -- git tag release
```

### 6. Build the container image locally (Alice)

Alice can now build the container image.

```shell
in-toto-record start -n build-image -k ../alice -m git:commit git:tag:release
docker build . -f Containerfile --tag ite-4-demo
in-toto-record stop -n build-image -k ../alice -p docker://ite-4-demo
```

### 7. Verify the workflow (Client)

Copy the layout and the links to a new directory to verify the integrity of the
workflow.

```shell
cd ../..
mkdir final_product
cp functionary_bob/project/*.link final_product
cp owner_alice/project/*.link final_product
cp owner_alice/root.layout final_product
cd final_product
in-toto-verify --layout root.layout --layout-key ../owner_alice/alice.pub
```
## Cleaning up and automated run through

### Clean slate

If you want to run the demo again, remove all the files and reset all of the
repos by running the following script.

```shell
python3 run_demo.py --clean
```

### Automated run through

Use the same script to have an automated run through of the demo.

```shell
python3 run_demo.py
```
