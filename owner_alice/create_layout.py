from securesystemslib import interface
from in_toto.models.layout import Layout
from in_toto.models.metadata import Metablock

def main():
  # Load Alice's private key to later sign the layout
  key_alice = interface.import_rsa_privatekey_from_file("alice")
  # Fetch and load Bob's and Carl's public keys
  # to specify that they are authorized to perform certain step in the layout
  key_bob = interface.import_rsa_publickey_from_file("../functionary_bob/bob.pub")

  layout = Layout.read({
      "_type": "layout",
      "keys": {
          key_bob["keyid"]: key_bob,
      },
      "steps": [{
          "name": "update-version",
          "expected_materials": [["ALLOW", "foo.py"], ["ALLOW", "*"]],
          "expected_products": [["MODIFY", "foo.py"]],
          "pubkeys": [key_bob["keyid"]],
          "expected_command": [],
          "threshold": 1,
        },{
          "name": "pull-request",
          "expected_materials": [["MATCH", "*", "WITH", "PRODUCTS", "FROM",
                                  "update-version"]],
          "expected_products": [["ALLOW", "*"]],
          "pubkeys": [key_bob["keyid"]],
          "expected_command": [],
          "threshold": 1,
        },{
          "name": "merge-pr",
          "expected_materials": [["ALLOW", "*"]],
          "expected_products": [["ALLOW", "*"]],
          "pubkeys": [key_alice["keyid"]],
          "expected_command": [],
          "threshold": 1,
        },{
          "name": "tag",
          "expected_materials": [["ALLOW", "*"]],
          "expected_products": [["ALLOW", "*"]],
          "pubkeys": [key_alice["keyid"]],
          "expected_command": [],
          "threshold": 1,
        }],
      "inspect":[],
  })

  metadata = Metablock(signed=layout)

  # Sign and dump layout to "root.layout"
  metadata.sign(key_alice)
  metadata.dump("root.layout")
  print('Created demo in-toto layout as "root.layout".')

if __name__ == '__main__':
  main()
