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
            "name":
            "commit-changes",
            "expected_materials": [["REQUIRE", "git:commit"],
                                   ["DISALLOW", "*"]],
            "expected_products": [["MODIFY", "git:commit"], ["DISALLOW", "*"]],
            "pubkeys": [pub_key_bob["keyid"]],
            "expected_command": [],
            "threshold":
            1,
        }, {
            "name":
            "open-pr",
            "expected_materials": [[
                "MATCH", "git:commit", "WITH", "PRODUCTS", "FROM",
                "commit-changes"
            ], ["DISALLOW", "*"]],
            "expected_products": [["CREATE", "github:*"], ["DISALLOW", "*"]],
            "pubkeys": [pub_key_bob["keyid"]],
            "expected_command": [],
            "threshold":
            1,
        }, {
            "name":
            "merge-pr",
            "expected_materials":
            [["MATCH", "github:*", "WITH", "PRODUCTS", "FROM", "open-pr"],
             ["MATCH", "git:commit", "WITH", "MATERIALS", "FROM", "open-pr"],
             ["DISALLOW", "*"]],
            "expected_products": [["MODIFY", "git:commit"], ["DISALLOW", "*"]],
            "pubkeys": [pub_key_alice["keyid"]],
            "expected_command": [],
            "threshold":
            1,
        }, {
            "name":
            "tag",
            "expected_materials":
            [["MATCH", "git:commit", "WITH", "PRODUCTS", "FROM", "merge-pr"],
             ["DISALLOW", "*"]],
            "expected_products": [["CREATE", "git:tag:*"], ["DISALLOW", "*"]],
            "pubkeys": [pub_key_alice["keyid"]],
            "expected_command": [],
            "threshold":
            1,
        }, {
            "name":
            "build-image",
            "expected_materials":
            [["MATCH", "git:commit", "WITH", "PRODUCTS", "FROM", "merge-pr"],
             ["MATCH", "git:tag:*", "WITH", "PRODUCTS", "FROM", "tag"],
             ["DISALLOW", "*"]],
            "expected_products": [["CREATE", "docker://*"], ["DISALLOW", "*"]],
            "pubkeys": [pub_key_alice["keyid"]],
            "expected_command": [],
            "threshold":
            1,
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
