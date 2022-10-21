if [[ "$TESTREPO" = "" ]]; then
    TESTREPO=git@github.com:in-toto/ite-4-demo-test-repo.git
fi

# Install demo dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install monkey-patched in-toto
git submodule update --init
cd in-toto
pip install .
cd ..

# Setup test projects for demo
git clone $TESTREPO owner_alice/project
git clone $TESTREPO functionary_bob/project

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "github-cli not installed"
    echo "Checkout https://cli.github.com/manual/installation for instructions"
fi

echo "Make sure to run 'source venv/bin/activate' before starting the demo!"
