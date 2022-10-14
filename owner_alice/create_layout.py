from securesystemslib import interface
from in_toto.models.layout import Layout
from in_toto.models.metadata import Metablock


def main():
    # Load Alice's private key to later sign the layout
    priv_key_alice = interface.import_rsa_privatekey_from_file("alice")

    # Load public keys
    pub_key_alice = interface.import_rsa_publickey_from_file(
        "../functionary_bob/bob.pub")
    pub_key_bob = interface.import_rsa_publickey_from_file("alice.pub")

    layout = Layout.read({
        "_type":
        "layout",
        "keys": {
            pub_key_alice["keyid"]: pub_key_alice,
            pub_key_bob["keyid"]: pub_key_bob,
        },
        "steps": [{
            "name": "update-version",
            "expected_materials": [["ALLOW", "foo.py"], ["ALLOW", "*"]],
            "expected_products": [["MODIFY", "foo.py"]],
            "pubkeys": [pub_key_bob["keyid"]],
            "expected_command": [],
            "threshold": 1,
        }, {
            "name":
            "pull-request",
            "expected_materials":
            [["MATCH", "*", "WITH", "PRODUCTS", "FROM", "update-version"]],
            "expected_products": [["ALLOW", "*"]],
            "pubkeys": [pub_key_bob["keyid"]],
            "expected_command": [],
            "threshold":
            1,
        }, {
            "name": "merge-pr",
            "expected_materials": [["ALLOW", "*"]],
            "expected_products": [["ALLOW", "*"]],
            "pubkeys": [pub_key_alice["keyid"]],
            "expected_command": [],
            "threshold": 1,
        }, {
            "name": "tag",
            "expected_materials": [["ALLOW", "*"]],
            "expected_products": [["ALLOW", "*"]],
            "pubkeys": [pub_key_alice["keyid"]],
            "expected_command": [],
            "threshold": 1,
        }],
        "inspect": [],
    })

    metadata = Metablock(signed=layout)

    # Sign and dump layout to "root.layout"
    metadata.sign(priv_key_alice)
    metadata.dump("root.layout")
    print('Created in-toto layout as "root.layout".')


if __name__ == '__main__':
    main()
