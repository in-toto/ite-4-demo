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
```


## Run the demo commands

### Define software supply chain layout (Alice)

```bash
cd owner_alice
python create_layout.py
```

### Clone project source code (Bob)
Since we don't have this project yet, we need to clone it first. But in the real world, it is more likely that Bob already has the project locally.

```bash
cd ../functionary_bob
git clone https://github.com/in-toto/ite-4-demo-test-repo.git
```

### Update version number (Bob)
Before Bob start making changes, Bob will create a `feature` branch
```
cd ite-4-demo-test-repo
git checkout -b feature
```
Bob uses `in-toot-record` command to records the state of the files he will modify. The material will be previous merged commit.
```
in-toto-record start --step-name update-version --key ../bob -m {github:SolidifiedRay/ITE-4-demo-test:commit:f1e5a041aa6cf8117b4290e9be091857bdee0aac}
```

Then Bob uses an editor of his choice to update the version number in `foo.py`
```
sed -i.bak 's/v0/v1/' foo.py && rm foo.py.bak
```

Finally, Bob records the state of the files after the modification
```
in-toto-record stop --step-name update-version --key ..bob -p foo.py
```

### Submit a pull request (Bob)
Bob has done his work and he will make a commit and push to the repo
```
git add foo.py
git commit -m "Update version number"
git push
```

Then Bob submit a pull request using github cli tool and use `in-toto-run` to record the state of the files
```
gh pr create --title "Update Version" --body "Update Version"
in-toto-run -n pull-request -m  . -p github:in-toto/ite-4-demo-test-repo:pr:{pr number} --key ../bob --no-command
```

### Approve and merge PR (Alice)
Now Alice will review Bob's PR, approve it and merged it
```
gh pr merge {pr number}
in-toto-run -n merge-pr -m . -p . --key alice --no-command
```

### Create a tag (Alice)
Then Alice will create a tag and release it
```
in-toto-run -n tag -m . -p . —key alice — git tag v 1.1
```
