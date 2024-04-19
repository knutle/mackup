import unittest
from mackup import main, utils
import os.path
import tempfile
from unittest.mock import patch
import sys


class TestMain(unittest.TestCase):
    def setUp(self):
        realpath = os.path.dirname(os.path.realpath(__file__))
        fixtures_path = os.path.join(realpath, "fixtures")

        mackup_config_fixture = os.path.join(fixtures_path, "mackup-copy-only.cfg")
        library_fixture = os.path.join(fixtures_path, "Library")
        
        temp_home = tempfile.mkdtemp()

        temp_config_path = os.path.join(temp_home, ".mackup.cfg")
        temp_library_path = os.path.join(temp_home, "Library")
        temp_mackup_path = os.path.join(temp_home, "Backups/Mackup")

        os.makedirs(temp_mackup_path)
        
        utils.copy(mackup_config_fixture, temp_config_path)
        utils.copy(library_fixture, temp_library_path)

        self.temp_home = temp_home
        self.fixtures_path = fixtures_path

    def tearDown(self):
        # clear all mocks
        patch.stopall()

        # cleanup temp dir
        utils.delete(self.temp_home)
        
    def test_main_header(self):
        assert main.header("blah") == "\033[34mblah\033[0m"

    def test_main_bold(self):
        assert main.bold("blah") == "\033[1mblah\033[0m"

    def test_main_backup_restore_with_copy_only(self):
        fake_args = ['mackup', '--copy-only', 'backup']
        
        with patch.object(sys, 'argv', fake_args), patch.dict(os.environ, {'HOME': self.temp_home}):
            main.main()

            assert not os.path.exists(os.path.join(self.fixtures_path, "Backups/Mackup"))
            assert not os.path.exists(os.path.join(self.fixtures_path, ".mackup.cfg"))

            assert os.path.isfile(os.path.join(self.temp_home, "Backups/Mackup/Library/Application Support/Sublime Text/Packages/User/Preferences.sublime-settings"))
            assert not os.path.exists(os.path.join(self.temp_home, "Backups/Mackup/Library/Application Support/Sublime Text/Packages/Default/Preferences.sublime-settings"))

        utils.delete(os.path.join(self.temp_home, "Library/Application Support/Sublime Text/Packages/User/Preferences.sublime-settings"))

        fake_args = ['mackup', '--copy-only', 'restore']
        
        with patch.object(sys, 'argv', fake_args), patch.dict(os.environ, {'HOME': self.temp_home}):
            assert not os.path.exists(os.path.join(self.temp_home, "Library/Application Support/Sublime Text/Packages/User/Preferences.sublime-settings"))

            main.main()

            assert not os.path.exists(os.path.join(self.fixtures_path, "Backups/Mackup"))
            assert not os.path.exists(os.path.join(self.fixtures_path, ".mackup.cfg"))

            assert os.path.isfile(os.path.join(self.temp_home, "Backups/Mackup/Library/Application Support/Sublime Text/Packages/User/Preferences.sublime-settings"))
            assert os.path.isfile(os.path.join(self.temp_home, "Library/Application Support/Sublime Text/Packages/User/Preferences.sublime-settings"))

        utils.delete(os.path.join(self.temp_home, "Library/Application Support/Sublime Text/Packages/User/Preferences.sublime-settings"))

    def test_main_uninstall_is_unaffected_by_copy_only(self):
        fake_args = ['mackup', 'backup']
        
        with patch.object(sys, 'argv', fake_args), patch.dict(os.environ, {'HOME': self.temp_home}):
            main.main()

            assert not os.path.exists(os.path.join(self.fixtures_path, "Backups/Mackup"))
            assert not os.path.exists(os.path.join(self.fixtures_path, ".mackup.cfg"))

            assert os.path.isfile(os.path.join(self.temp_home, "Backups/Mackup/Library/Application Support/Sublime Text/Packages/User/Preferences.sublime-settings"))
            assert os.path.islink(os.path.join(self.temp_home, "Library/Application Support/Sublime Text/Packages/User"))

        fake_args = ['mackup', '--copy-only', '--force', 'uninstall']
        
        with patch.object(sys, 'argv', fake_args), patch.dict(os.environ, {'HOME': self.temp_home}):
            main.main()

            assert not os.path.exists(os.path.join(self.fixtures_path, "Backups/Mackup"))
            assert not os.path.exists(os.path.join(self.fixtures_path, ".mackup.cfg"))

            assert os.path.isfile(os.path.join(self.temp_home, "Backups/Mackup/Library/Application Support/Sublime Text/Packages/User/Preferences.sublime-settings"))
            assert os.path.isfile(os.path.join(self.temp_home, "Library/Application Support/Sublime Text/Packages/User/Preferences.sublime-settings"))

        # reset force constant on utils manually to avoid persisting changes in outer scope
        utils.FORCE_YES = False

    def test_main_backup_restore_default_behavior(self):
        assert not os.path.exists(os.path.join(self.temp_home, "Backups/Mackup/Library/Application Support/Sublime Text/Packages/User/Preferences.sublime-settings"))
        assert os.path.isfile(os.path.join(self.temp_home, "Library/Application Support/Sublime Text/Packages/User/Preferences.sublime-settings"))

        utils.delete(os.path.join(self.temp_home, "Backups/Mackup/Library/Application Support/Sublime Text/Packages/User/Preferences.sublime-settings"))

        fake_args = ['mackup', 'backup']
        
        with patch.object(sys, 'argv', fake_args), patch.dict(os.environ, {'HOME': self.temp_home}):
            main.main()

            assert os.path.isfile(os.path.join(self.temp_home, "Backups/Mackup/Library/Application Support/Sublime Text/Packages/User/Preferences.sublime-settings"))
            assert os.path.islink(os.path.join(self.temp_home, "Library/Application Support/Sublime Text/Packages/User"))

        fake_args = ['mackup', '--force', 'restore']
        
        with patch.object(sys, 'argv', fake_args), patch.dict(os.environ, {'HOME': self.temp_home}):
            assert os.path.islink(os.path.join(self.temp_home, "Library/Application Support/Sublime Text/Packages/User"))

            main.main()

            assert os.path.isfile(os.path.join(self.temp_home, "Backups/Mackup/Library/Application Support/Sublime Text/Packages/User/Preferences.sublime-settings"))
            assert os.path.islink(os.path.join(self.temp_home, "Library/Application Support/Sublime Text/Packages/User"))

        # reset force constant on utils manually to avoid persisting changes in outer scope
        utils.FORCE_YES = False

        utils.delete(os.path.join(self.temp_home, "Library/Application Support/Sublime Text/Packages/User"))

        fake_args = ['mackup', 'restore']
        
        with patch.object(sys, 'argv', fake_args), patch.dict(os.environ, {'HOME': self.temp_home}):
            main.main()

            assert os.path.isfile(os.path.join(self.temp_home, "Backups/Mackup/Library/Application Support/Sublime Text/Packages/User/Preferences.sublime-settings"))
            assert os.path.islink(os.path.join(self.temp_home, "Library/Application Support/Sublime Text/Packages/User"))

        # reset force constant on utils manually to avoid persisting changes in outer scope
        utils.FORCE_YES = False
