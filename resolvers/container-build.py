"""
ITE-4:

ITE-4 Resolver for container GH action build.
"""

import json
import sys

import securesystemslib.formats
import securesystemslib.hash


def digest_image(standard, tag, digest_algorithm, digest_value,
                 hash_algorithms):
    if standard not in ['docker', 'oci']:
        sys.exit(f"{standard} is not a recognized container standard")

    if not hash_algorithms:
        hash_algorithms = ['sha256']

    securesystemslib.formats.HASHALGORITHMS_SCHEMA.check_match(hash_algorithms)
    hash_dict = {}

    for algorithm in hash_algorithms:
        digest_object = securesystemslib.hash.digest(
            algorithm, securesystemslib.hash.DEFAULT_HASH_LIBRARY)

        representation = {
            f'{standard}://{tag}': {
                digest_algorithm: digest_value
            }
        }

        digest_object.update(
            json.dumps(representation, sort_keys=True).encode())
        hash_dict.update({algorithm: digest_object.hexdigest()})

    return hash_dict


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(f'Error: Usage: {sys.argv[0]} <standard> <tag> <digest>')

    digest_algorithm, digest_value = sys.argv[3].split(':')
    hash_algorithms = ['sha256', 'sha512', 'md5']
    generated_hash = digest_image(sys.argv[1], sys.argv[2], digest_algorithm,
                                  digest_value, hash_algorithms)

    print(json.dumps(generated_hash, indent=4))
