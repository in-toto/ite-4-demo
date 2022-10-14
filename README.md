# ITE-4-demo

## Demo setup

For this demo, you may need to install [github cli tool](https://cli.github.com/)

Install the monkey patch version of in-toto

```bash
git clone https://github.com/SolidifiedRay/in-toto.git -b ITE-4-monkey-patch
pip install -r requirements.txt
```

Get demo files
```bash
git clone https://github.com/in-toto/ite-4-demo.git
cd ite-4-demo
```


## Run the demo commands

### Clone project source code (Bob & Alice)
Since we don't have this project yet, we need to clone it first. But in the real world, it is more likely that Bob and Alice already has the project locally.

```bash
cd functionary_bob
git clone https://github.com/in-toto/ite-4-demo-test-repo.git

cd ../owner_alice
git clone https://github.com/in-toto/ite-4-demo-test-repo.git
```

### Define software supply chain layout (Alice)

```bash
python create_layout.py
```

### Update version number (Bob)
Before Bob start making changes, Bob will create a `feature` branch
```
cd ../functionary_bob/ite-4-demo-test-repo

git checkout -b feature
```

Bob uses `in-toot-record` command to records the state of the files he will modify. The material will be previous merged commit.
```shell
# We use a generic uri to represent a Github entity
# A github commit looks like: github:org/repo:commit:id

in-toto-record start --step-name update-version --key ../bob -m github:in-toto/ite-4-demo-test-repo:commit:{previously merged commit id}
```

Then Bob uses an editor of his choice to update the version number in `foo.py`
```
sed -i.bak 's/v0/v1/' foo.py && rm foo.py.bak
```

Finally, Bob records the state of the files after the modification and produces a link metadata file called `update-version.[Bob's keyid].link`.
```
in-toto-record stop --step-name update-version --key ../bob -p foo.py
```

### Submit a pull request (Bob)
Bob has done his work and he will make a commit and push to the repo
```
git add foo.py
git commit -m "Update version"
git push --set-upstream origin feature
```

Then Bob submit a pull request using github cli tool and use `in-toto-run` to record the state of the files
```
gh pr create --title "Update version" --body "Update version number"
in-toto-run -n pull-request -m  . -p github:in-toto/ite-4-demo-test-repo:pr:{pr number} --key ../bob --no-command
```

### Approve and merge PR (Alice)
Now Alice will review Bob's PR, approve it and merged it
```
cd ../../owner_alice/ite-4-demo-test-repo
gh pr merge {pr number}
in-toto-run -n merge-pr -m . -p . --key ../alice --no-command
```

### Create a tag (Alice)
Then Alice will create a tag and release it
```
in-toto-run -n tag -m . -p . --key ../alice -- git tag v 0.1
```
