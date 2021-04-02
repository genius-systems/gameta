import zipfile
from os import listdir
from os.path import join, dirname, basename, exists
from shutil import copytree, copyfile
from unittest import TestCase

from click.testing import CliRunner

from gameta.base.errors import VCSError
from gameta.base.vcs.git import Git, GitRepo


class TestGit(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.git = Git

    def test_git_is_vcs_type_folder_is_git_repo(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            self.assertTrue(self.git.is_vcs_type(f))

    def test_git_is_vcs_type_folder_is_not_git_repo(self):
        with self.runner.isolated_filesystem() as f:
            self.assertFalse(self.git.is_vcs_type(f))

    def test_git_generate_repo_git_repo_available(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            test_repo = self.git.generate_repo(f)
            self.assertIsInstance(test_repo, GitRepo)
            self.assertEqual(test_repo.path, f)
            self.assertEqual(test_repo.name, 'gameta')
            self.assertTrue(
                test_repo.url in
                [
                    'http://github.com/genius-systems/gameta.git',
                    'git@github.com:genius-systems/gameta.git'
                ]
            )

    def test_git_generate_repo_path_does_not_exist(self):
        with self.assertRaises(VCSError):
            self.git.generate_repo('invalid_dir')

    def test_git_generate_repo_path_is_not_git_repo(self):
        with self.runner.isolated_filesystem() as f:
            with self.assertRaises(VCSError):
                self.git.generate_repo(f)

    def test_git_init_path_created_by_init(self):
        with self.runner.isolated_filesystem() as f:
            test_repo = self.git.init(join(f, 'this', 'is', 'an', 'invalid_dir'))
            self.assertIsInstance(test_repo, GitRepo)
            self.assertEqual(test_repo.path, join(f, 'this', 'is', 'an', 'invalid_dir'))
            self.assertEqual(test_repo.name, 'invalid_dir')
            self.assertIsNone(test_repo.url)
            self.assertEqual(test_repo.branch, 'master')
            self.assertIsNone(test_repo.hash)

    def test_git_init_path_is_not_git_repo(self):
        with self.runner.isolated_filesystem() as f:
            test_repo = self.git.init(f)
            self.assertIsInstance(test_repo, GitRepo)
            self.assertEqual(test_repo.path, f)
            self.assertEqual(test_repo.name, basename(f))
            self.assertIsNone(test_repo.url)
            self.assertEqual(test_repo.branch, 'master')
            self.assertIsNone(test_repo.hash)

    def test_git_init_path_is_git_repo(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            test_repo = self.git.init(f)
            self.assertIsInstance(test_repo, GitRepo)
            self.assertEqual(test_repo.path, f)
            self.assertEqual(test_repo.name, basename(f))
            self.assertIsNone(test_repo.url)

    def test_git_clone_url_not_provided(self):
        with self.runner.isolated_filesystem() as f:
            with self.assertRaisesRegex(VCSError, 'URL .* is invalid'):
                self.git.clone(f, '')

    def test_git_clone_invalid_url_provided(self):
        with self.runner.isolated_filesystem() as f:
            with self.assertRaisesRegex(VCSError, 'Could not initialise git repository'):
                self.git.clone(f, 'this/is/an/invalid/url')

    def test_git_clone_repository_cloned(self):
        with self.runner.isolated_filesystem() as f:
            test_repo = self.git.clone(f, 'http://github.com/genius-systems/gameta.git')
            self.assertIsInstance(test_repo, GitRepo)
            self.assertEqual(test_repo.path, f)
            self.assertEqual(test_repo.name, 'gameta')
            self.assertEqual(test_repo.url, 'http://github.com/genius-systems/gameta.git')
            self.assertEqual(test_repo.branch, 'master')

    def test_git_clone_path_is_git_repo(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            with self.assertRaisesRegex(VCSError, 'Could not initialise git repository .*'):
                self.git.clone(f, 'http://github.com/genius-systems/gameta.git')


class TestGitRepo(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.git = Git

    def test_git_repo_create_no_gitignore(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            test_repo = Git.generate_repo(f)
            self.assertEqual(test_repo.ignore_data, [])
            self.assertEqual(test_repo.path, f)
            self.assertEqual(test_repo.name, 'gameta')
            self.assertIsNotNone(test_repo.branch)
            self.assertIsNotNone(test_repo.hash)
            self.assertIsNotNone(test_repo.url)

    def test_git_repo_create_with_gitignore(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            copyfile(join(dirname(dirname(dirname(__file__))), 'data', '.gitignore'), join(f, '.gitignore'))
            test_repo = Git.generate_repo(f)
            self.assertEqual(len(test_repo.ignore_data), 132)
            self.assertEqual(test_repo.path, f)
            self.assertEqual(test_repo.name, 'gameta')
            self.assertIsNotNone(test_repo.branch)
            self.assertIsNotNone(test_repo.hash)
            self.assertIsNotNone(test_repo.url)

    def test_git_repo_ignore_no_files_no_gitignore_file(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            test_repo = Git.generate_repo(f)
            test_repo.ignore([])
            self.assertEqual(test_repo.ignore_data, [])
            self.assertTrue(exists(join(f, '.gitignore')))
            with open(join(f, '.gitignore'), 'r') as g:
                self.assertEqual(g.readlines(), [])

    def test_git_repo_ignore_files_no_gitignore_file(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            test_repo = Git.generate_repo(f)
            test_repo.ignore(['a.txt', 'b.txt'])
            self.assertEqual(test_repo.ignore_data, ['a.txt\n', 'b.txt\n'])
            self.assertTrue(exists(join(f, '.gitignore')))
            with open(join(f, '.gitignore'), 'r') as g:
                self.assertEqual(g.readlines(), ['a.txt\n', 'b.txt\n'])

    def test_git_repo_ignore_no_files_gitignore_file(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            copyfile(join(dirname(dirname(dirname(__file__))), 'data', '.gitignore'), join(f, '.gitignore'))
            test_repo = Git.generate_repo(f)
            test_repo.ignore([])
            self.assertEqual(len(test_repo.ignore_data), 132)
            self.assertTrue(exists(join(f, '.gitignore')))
            with open(join(f, '.gitignore'), 'r') as g:
                self.assertEqual(len(g.readlines()), 132)

    def test_git_repo_ignore_files_gitignore_file(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            copyfile(join(dirname(dirname(dirname(__file__))), 'data', '.gitignore'), join(f, '.gitignore'))
            test_repo = Git.generate_repo(f)
            test_repo.ignore(['a.txt', 'b.txt'])
            self.assertEqual(len(test_repo.ignore_data), 134)
            self.assertEqual(test_repo.ignore_data[-2:], ['a.txt\n', 'b.txt\n'])
            self.assertTrue(exists(join(f, '.gitignore')))
            with open(join(f, '.gitignore'), 'r') as g:
                output = g.readlines()
                self.assertEqual(len(output), 134)
                self.assertEqual(output[-2:], ['a.txt\n', 'b.txt\n'])

    def test_git_repo_fetch_all_updates(self):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(dirname(dirname(__file__))), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            test_repo = Git.generate_repo(join(f, 'GitPython'))
            before_fetch = test_repo.repo.references
            test_repo.fetch()
            after_fetch = test_repo.repo.references
            self.assertNotEqual(len(before_fetch), len(after_fetch))

    def test_git_repo_switch_to_non_existent_branch(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            test_repo = Git.generate_repo(f)
            test_repo.switch('new_branch')
            self.assertTrue('new_branch' in [str(i) for i in test_repo.repo.branches])
            self.assertTrue(test_repo.repo.head.reference.name == test_repo.branch == 'new_branch')
            self.assertEqual(test_repo.repo.commit().hexsha, test_repo.hash)

    def test_git_repo_switch_to_existing_branch(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            test_repo = Git.generate_repo(f)
            self.assertTrue('master' in [str(i) for i in test_repo.repo.branches])
            test_repo.switch('master')
            self.assertTrue(test_repo.repo.head.reference.name == test_repo.branch == 'master')
            self.assertEqual(test_repo.repo.commit().hexsha, test_repo.hash)

    def test_git_repo_switch_to_existing_git_reference(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            test_repo = Git.generate_repo(f)
            old_hash = test_repo.hash
            test_repo.switch('HEAD~2')
            self.assertTrue(test_repo.repo.head.reference.name == test_repo.branch == 'HEAD~2')
            self.assertTrue(test_repo.repo.commit().hexsha == test_repo.hash != old_hash)

    def test_git_repo_update_code_remote_does_not_exist(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            test_repo = Git.generate_repo(f)
            with self.assertRaisesRegex(VCSError, 'test does not exist'):
                test_repo.update('test')

    def test_git_repo_update_code_branch_does_not_exist(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            test_repo = Git.generate_repo(f)
            with self.assertRaisesRegex(VCSError, 'invalid_branch does not exist in remote source origin'):
                test_repo.update(branch='invalid_branch')

    def test_git_repo_update_code_from_unrelated_histories(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            test_repo = Git.generate_repo(f)
            with self.assertRaisesRegex(VCSError, 'refusing to merge unrelated histories'):
                test_repo.update(branch='gh-pages')

    def test_git_repo_update_code(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            test_repo = Git.generate_repo(f)
            self.assertListEqual(listdir(f), ['.git'])
            test_repo.switch('master')
            test_repo.update()
            self.assertListEqual(
                listdir(f),
                [
                    'tests', 'pyproject.toml', 'gameta', 'docs', 'README.md', 'LICENSE', '.gitignore',
                    '.github', '.circleci', '.git'
                ]
            )

    def test_git_repo_remove_ignore_files_not_found(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            copyfile(join(dirname(dirname(dirname(__file__))), 'data', '.gitignore'), join(f, '.gitignore'))
            test_repo = Git.generate_repo(f)
            self.assertEqual(len(test_repo.ignore_data), 132)
            test_repo.remove_ignore(['test', 'hello', 'world'])
            self.assertEqual(len(test_repo.ignore_data), 132)
            with open(join(f, '.gitignore')) as g:
                self.assertEqual(len(g.readlines()), 132)

    def test_git_repo_remove_ignore_files_exist(self):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(dirname(dirname(__file__)))), '.git'), join(f, '.git'))
            copyfile(join(dirname(dirname(dirname(__file__))), 'data', '.gitignore'), join(f, '.gitignore'))
            test_repo = Git.generate_repo(f)
            self.assertEqual(len(test_repo.ignore_data), 132)
            test_repo.remove_ignore(['__pycache__/', '.idea', '.pyre/'])
            self.assertEqual(len(test_repo.ignore_data), 129)
            with open(join(f, '.gitignore')) as g:
                test_output = g.readlines()
                self.assertEqual(len(test_output), 129)
                self.assertNotIn('__pycache__/\n', test_output)
                self.assertNotIn('.idea\n', test_output)
                self.assertNotIn('.pyre/\n', test_output)
