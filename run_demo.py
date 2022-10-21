import os
import re
import sys
import shlex
import subprocess
import argparse
from shutil import copyfile, rmtree

NO_PROMPT = False
TESTREPO = "in-toto/ite-4-demo-test-repo"


def prompt_key(prompt):
    if NO_PROMPT:
        print("\n" + prompt)
        return
    inp = False
    while inp != "":
        try:
            inp = input("\n{} -- press any key to continue".format(prompt))
        except Exception:
            pass


def supply_chain():

    prompt_key("Define the supply chain layout (Alice)")
    os.chdir("owner_alice")
    create_layout_cmd = "python create_layout.py"
    print(create_layout_cmd)
    subprocess.call(shlex.split(create_layout_cmd))

    prompt_key("Make and commit changes to the project (Bob)")
    os.chdir("../functionary_bob/project")
    checkout_new_branch_cmd = "git checkout -b feature"
    print(checkout_new_branch_cmd)
    subprocess.call(shlex.split(checkout_new_branch_cmd))

    make_commit_changes_start_cmd = ("in-toto-record"
                                     " start"
                                     " --verbose"
                                     " --step-name commit-changes"
                                     " --key ../bob"
                                     " --materials git:commit")
    print(make_commit_changes_start_cmd)
    subprocess.call(shlex.split(make_commit_changes_start_cmd))

    make_changes_cmd = r"perl -i -p -e 's/(\d+)/$1 + 1/eg' foo.py"
    print(make_changes_cmd)
    subprocess.call(shlex.split(make_changes_cmd))

    add_changes_cmd = "git add foo.py"
    print(add_changes_cmd)
    subprocess.call(shlex.split(add_changes_cmd))

    commit_changes_cmd = "git commit -m 'update version'"
    print(commit_changes_cmd)
    subprocess.call(shlex.split(commit_changes_cmd))

    make_commit_changes_stop_cmd = ("in-toto-record"
                                    " stop"
                                    " --verbose"
                                    " --step-name commit-changes"
                                    " --key ../bob"
                                    " --products git:commit")
    print(make_commit_changes_stop_cmd)
    subprocess.call(shlex.split(make_commit_changes_stop_cmd))

    prompt_key("Create a Pull Request (Bob)")
    push_changes_cmd = "git push --set-upstream origin feature"
    print(push_changes_cmd)
    subprocess.call(shlex.split(push_changes_cmd))

    create_pr_start_cmd = ("in-toto-record"
                           " start"
                           " --verbose"
                           " --step-name create-pr"
                           " --key ../bob"
                           " --materials git:commit")
    print(create_pr_start_cmd)
    subprocess.call(shlex.split(create_pr_start_cmd))

    create_pr_cmd = ("gh pr create"
                     " --title 'update version'"
                     " --body 'update version number'")
    print(create_pr_cmd)
    pr_link = subprocess.check_output(shlex.split(create_pr_cmd))
    pr_number = pr_link.decode().replace('\n', '').split('/')[-1]

    create_pr_stop_cmd = ("in-toto-record"
                          " stop"
                          " --verbose"
                          " --step-name create-pr"
                          " --key ../bob"
                          f" --products github:{TESTREPO}:pr:{pr_number}")
    print(create_pr_stop_cmd)
    subprocess.call(shlex.split(create_pr_stop_cmd))

    prompt_key("Approve and merge PR (Alice)")
    os.chdir("../../owner_alice/project")
    merge_pr_start_cmd = (
        "in-toto-record"
        " start"
        " --verbose"
        " --step-name merge-pr"
        " --key ../alice"
        f" --materials github:{TESTREPO}:pr:{pr_number} git:commit")
    print(merge_pr_start_cmd)
    subprocess.call(shlex.split(merge_pr_start_cmd))

    merge_pr_cmd = f"gh pr merge {pr_number}"
    print(merge_pr_cmd)
    subprocess.call(shlex.split(merge_pr_cmd))

    pull_merge_commit_cmd = "git pull"
    print(pull_merge_commit_cmd)
    subprocess.call(shlex.split(pull_merge_commit_cmd))

    merge_pr_stop_cmd = ("in-toto-record"
                         " stop"
                         " --verbose"
                         " --step-name merge-pr"
                         " --key ../alice"
                         " --products git:commit")
    print(merge_pr_stop_cmd)
    subprocess.call(shlex.split(merge_pr_stop_cmd))

    prompt_key("Create a Tag (Alice)")
    tag_cmd = ("in-toto-run"
               " --verbose"
               " --step-name tag"
               " --key ../alice"
               " --materials git:commit"
               " --products git:tag:release"
               " -- git tag release")
    print(tag_cmd)
    subprocess.call(shlex.split(tag_cmd))

    prompt_key("Build the container image (Alice)")
    build_container_start_cmd = ("in-toto-record"
                                 " start"
                                 " --verbose"
                                 " --step-name build-image"
                                 " --key ../alice"
                                 " --materials git:commit git:tag:release")
    print(build_container_start_cmd)
    subprocess.call(shlex.split(build_container_start_cmd))

    build_container_cmd = ("docker build ."
                           " --file Containerfile"
                           " --tag ite-4-demo")
    print(build_container_cmd)
    subprocess.call(shlex.split(build_container_cmd))

    build_container_stop_cmd = ("in-toto-record"
                                " stop"
                                " --verbose"
                                " --step-name build-image"
                                " --key ../alice"
                                " --products docker://ite-4-demo")
    print(build_container_stop_cmd)
    subprocess.call(shlex.split(build_container_stop_cmd))

    prompt_key("Create final product")
    os.chdir("../..")
    os.makedirs("final_product", exist_ok=True)
    copyfile("owner_alice/root.layout", "final_product/root.layout")
    copyfile("functionary_bob/project/commit-changes.776a00e2.link",
             "final_product/commit-changes.776a00e2.link")
    copyfile("functionary_bob/project/create-pr.776a00e2.link",
             "final_product/create-pr.776a00e2.link")
    copyfile("owner_alice/project/merge-pr.556caebd.link",
             "final_product/merge-pr.556caebd.link")
    copyfile("owner_alice/project/tag.556caebd.link",
             "final_product/tag.556caebd.link")
    copyfile("owner_alice/project/build-image.556caebd.link",
             "final_product/build-image.556caebd.link")

    prompt_key("Verify final product (Client)")
    os.chdir("final_product")
    copyfile("../owner_alice/alice.pub", "alice.pub")
    verify_cmd = ("in-toto-verify"
                  " --verbose"
                  " --layout root.layout"
                  " --layout-key alice.pub")
    print(verify_cmd)
    retval = subprocess.call(shlex.split(verify_cmd))
    print("Return value: " + str(retval))

    # ====================================================================
    # Tampering with the supply chain
    # ====================================================================

    prompt_key("Tamper with the supply chain (Adversary)")
    os.chdir("../owner_alice/project")
    tamper_cmd = "echo 'something evil' >> foo.py"
    print(tamper_cmd)
    subprocess.call(tamper_cmd, shell=True)

    print(add_changes_cmd)
    subprocess.call(shlex.split(add_changes_cmd))

    commit_malicious_change_cmd = "git commit --amend --no-edit"
    print(commit_malicious_change_cmd)
    subprocess.call(shlex.split(commit_malicious_change_cmd))

    prompt_key("[Continue as if nothing happened]\nCreate a Tag (Alice)")
    print(tag_cmd)
    subprocess.call(shlex.split(tag_cmd))

    prompt_key("Build the container image (Alice)")
    print(build_container_start_cmd)
    subprocess.call(shlex.split(build_container_start_cmd))

    print(build_container_cmd)
    subprocess.call(shlex.split(build_container_cmd))

    print(build_container_stop_cmd)
    subprocess.call(shlex.split(build_container_stop_cmd))

    prompt_key("Create final tampered product")
    os.chdir("../..")
    os.makedirs("final_product", exist_ok=True)
    copyfile("owner_alice/root.layout", "final_product/root.layout")
    copyfile("functionary_bob/project/commit-changes.776a00e2.link",
             "final_product/commit-changes.776a00e2.link")
    copyfile("functionary_bob/project/create-pr.776a00e2.link",
             "final_product/create-pr.776a00e2.link")
    copyfile("owner_alice/project/merge-pr.556caebd.link",
             "final_product/merge-pr.556caebd.link")
    copyfile("owner_alice/project/tag.556caebd.link",
             "final_product/tag.556caebd.link")
    copyfile("owner_alice/project/build-image.556caebd.link",
             "final_product/build-image.556caebd.link")

    prompt_key("Verify final tampered product (Client)")
    os.chdir("final_product")
    copyfile("../owner_alice/alice.pub", "alice.pub")
    print(verify_cmd)
    retval = subprocess.call(shlex.split(verify_cmd))
    print("Return value: " + str(retval))


def extract_repo(uri):
    ssh_pattern = r'^git@github.com:([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+).git$'
    repo = re.findall(ssh_pattern, uri)
    if len(repo) > 0:
        return repo[0]
    https_pattern = r'^https://github.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+).git$'
    repo = re.findall(https_pattern, uri)
    if len(repo) > 0:
        return repo[0]
    regular_pattern = r'^([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)$'
    repo = re.findall(regular_pattern, uri)
    if len(repo) > 0:
        return repo[0]
    sys.exit(f'failed to extract github repo from "{uri}"')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n",
                        "--no-prompt",
                        help="No prompt.",
                        action="store_true")
    parser.add_argument("-c",
                        "--clean",
                        help="Remove files created during demo.",
                        action="store_true")
    args = parser.parse_args()

    if repo := os.getenv("TESTREPO"):
        global TESTREPO
        TESTREPO = extract_repo(repo)
        print(TESTREPO)

    if args.clean:
        files_to_delete = [
            "owner_alice/root.layout",
            "owner_alice/project/merge-pr.556caebd.link",
            "owner_alice/project/tag.556caebd.link",
            "owner_alice/project/build-image.556caebd.link",
            "functionary_bob/project/commit-changes.776a00e2.link",
            "functionary_bob/project/create-pr.776a00e2.link",
            "final_product",
        ]

        for path in files_to_delete:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                rmtree(path)

        # reset project
        os.chdir("owner_alice/project")
        subprocess.call(shlex.split("git checkout main"))
        subprocess.call(shlex.split("git reset --hard"))
        subprocess.call(shlex.split("git pull -f"))
        os.chdir("../..")
        os.chdir("functionary_bob/project")
        subprocess.call(shlex.split("git checkout main"))
        subprocess.call(shlex.split("git reset --hard"))
        subprocess.call(shlex.split("git branch -D feature"))
        subprocess.call(shlex.split("git pull -f"))
        os.chdir("../..")

        sys.exit(0)
    if args.no_prompt:
        global NO_PROMPT
        NO_PROMPT = True

    supply_chain()


if __name__ == '__main__':
    main()
