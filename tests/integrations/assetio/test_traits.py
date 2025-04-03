#!/usr/bin/env python
# test_traits.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-03

"""
Tests for the OpenAssetIO trait handler.
"""

import unittest
from unittest.mock import MagicMock, patch

# Set up mocks for OpenAssetIO modules
with patch.dict('sys.modules', {
    'openassetio': MagicMock(),
    'openassetio.trait': MagicMock(),
}):
    # Now we can import our module that uses OpenAssetIO
    from bifrost.integrations.assetio.traits import BifrostTraitHandler, trait_handler


class MockAsset:
    """Mock asset class for testing."""
    
    def __init__(self, **kwargs):
        """Initialize with arbitrary attributes."""
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockDependency:
    """Mock dependency class for testing."""
    
    def __init__(self, dependent_asset_id, dependency_type=None, optional=False, metadata=None):
        """Initialize with dependency attributes."""
        self.dependent_asset_id = dependent_asset_id
        self.dependency_type = dependency_type
        self.optional = optional
        self.metadata = metadata or {}


class TestBifrostTraitHandler(unittest.TestCase):
    """Test the BifrostTraitHandler class."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a fresh instance for each test
        self.trait_handler = BifrostTraitHandler()
        
        # Override the enabled flag to ensure tests run
        self.trait_handler.enabled = True
        
    def test_expand_trait_set(self):
        """Test expansion of standard trait sets."""
        # Test basic set
        expanded = self.trait_handler._expand_trait_set(["basic"])
        self.assertEqual(expanded, {"locatableContent", "defaultName"})
        
        # Test mixed set
        expanded = self.trait_handler._expand_trait_set(["basic", "customTrait"])
        self.assertEqual(expanded, {"locatableContent", "defaultName", "customTrait"})
        
        # Test empty set
        expanded = self.trait_handler._expand_trait_set([])
        self.assertEqual(expanded, set())
        
    def test_set_nested_value(self):
        """Test setting nested values in trait dictionaries."""
        result = {}
        
        # Test simple case
        self.trait_handler._set_nested_value(result, "testTrait", "testProp", "testValue")
        self.assertEqual(result, {"testTrait": {"testProp": "testValue"}})
        
        # Test nested case
        self.trait_handler._set_nested_value(result, "nestedTrait", "level1.level2.level3", "nestedValue")
        self.assertEqual(
            result["nestedTrait"], 
            {"level1": {"level2": {"level3": "nestedValue"}}}
        )
        
    def test_get_nested_value(self):
        """Test getting nested values from trait dictionaries."""
        data = {
            "testTrait": {"testProp": "testValue"},
            "nestedTrait": {"level1": {"level2": {"level3": "nestedValue"}}}
        }
        
        # Test simple case
        value = self.trait_handler._get_nested_value(data, "testTrait", "testProp")
        self.assertEqual(value, "testValue")
        
        # Test nested case
        value = self.trait_handler._get_nested_value(data, "nestedTrait", "level1.level2.level3")
        self.assertEqual(value, "nestedValue")
        
        # Test missing trait
        value = self.trait_handler._get_nested_value(data, "missingTrait", "prop")
        self.assertIsNone(value)
        
        # Test missing property
        value = self.trait_handler._get_nested_value(data, "testTrait", "missingProp")
        self.assertIsNone(value)
        
        # Test missing nested property
        value = self.trait_handler._get_nested_value(data, "nestedTrait", "level1.missing.level3")
        self.assertIsNone(value)
        
    def test_discover_traits(self):
        """Test trait discovery from asset attributes."""
        # Create a mock asset with various attributes
        asset = MockAsset(
            name="Test Asset",
            description="Test description",
            path="/path/to/asset",
            version_number=1,
            created_at="2025-04-03",
            created_by="test_user",
            comment="Initial version"
        )
        
        # Discover traits
        traits = self.trait_handler.discover_traits(asset)
        
        # Check expected traits are present
        expected_traits = {"defaultName", "defaultDescription", "locatableContent", "versionedContent"}
        self.assertEqual(traits, expected_traits)
        
        # Test with media attributes
        asset = MockAsset(
            name="Test Media",
            path="/path/to/media",
            media_type="video",
            duration=120.5,
            frame_rate=24,
            width=1920,
            height=1080
        )
        
        traits = self.trait_handler.discover_traits(asset)
        self.assertIn("mediaSource", traits)
        
    def test_asset_to_traits_data(self):
        """Test conversion from asset to traits data."""
        # Create a mock asset
        asset = MockAsset(
            name="Test Asset",
            description="Test description",
            path="/path/to/asset",
            version_number=1,
            created_at="2025-04-03",
            created_by="test_user",
            comment="Initial version"
        )
        
        # Convert to traits data with versioned trait set
        traits_data = self.trait_handler.asset_to_traits_data(asset, ["versioned"])
        
        # Check expected traits and values
        self.assertIn("defaultName", traits_data)
        self.assertEqual(traits_data["defaultName"]["name"], "Test Asset")
        
        self.assertIn("defaultDescription", traits_data)
        self.assertEqual(traits_data["defaultDescription"]["description"], "Test description")
        
        self.assertIn("locatableContent", traits_data)
        self.assertEqual(traits_data["locatableContent"]["location"], "/path/to/asset")
        
        self.assertIn("versionedContent", traits_data)
        self.assertEqual(traits_data["versionedContent"]["version"], 1)
        self.assertEqual(traits_data["versionedContent"]["versionInfo"]["created"], "2025-04-03")
        self.assertEqual(traits_data["versionedContent"]["versionInfo"]["createdBy"], "test_user")
        self.assertEqual(traits_data["versionedContent"]["versionInfo"]["comment"], "Initial version")
        
    def test_traits_data_to_asset(self):
        """Test conversion from traits data to asset."""
        # Create traits data
        traits_data = {
            "defaultName": {"name": "Updated Asset"},
            "defaultDescription": {"description": "Updated description"},
            "locatableContent": {"location": "/updated/path"},
            "versionedContent": {
                "version": 2,
                "versionInfo": {
                    "created": "2025-04-04",
                    "createdBy": "other_user",
                    "comment": "Updated version"
                }
            }
        }
        
        # Create a mock asset
        asset = MockAsset()
        
        # Update asset from traits data
        updated_asset = self.trait_handler.traits_data_to_asset(traits_data, asset)
        
        # Check asset was updated with expected values
        self.assertEqual(updated_asset.name, "Updated Asset")
        self.assertEqual(updated_asset.description, "Updated description")
        self.assertEqual(updated_asset.path, "/updated/path")
        self.assertEqual(updated_asset.version_number, 2)
        self.assertEqual(updated_asset.created_at, "2025-04-04")
        self.assertEqual(updated_asset.created_by, "other_user")
        self.assertEqual(updated_asset.comment, "Updated version")
        
    def test_relationship_trait_discovery(self):
        """Test discovery of relationship traits."""
        # Create a mock asset with dependencies
        asset = MockAsset(
            name="Asset with Dependencies",
            dependencies=[
                MockDependency("dep1", "reference", False),
                MockDependency("dep2", "requires", True)
            ]
        )
        
        # Discover traits
        traits = self.trait_handler.discover_traits(asset)
        
        # Check relationship trait is present
        self.assertIn("relationshipManagement", traits)
        
        # Create a mock asset without dependencies
        asset = MockAsset(name="Asset without Dependencies")
        
        # Discover traits
        traits = self.trait_handler.discover_traits(asset)
        
        # Check relationship trait is not present
        self.assertNotIn("relationshipManagement", traits)
        
    def test_relationship_trait_export(self):
        """Test export of relationship traits."""
        # Create a mock asset with dependencies
        asset = MockAsset(
            name="Asset with Dependencies",
            dependencies=[
                MockDependency("dep1", "reference", False, {"purpose": "texture"}),
                MockDependency("dep2", "requires", True, {"purpose": "model"})
            ]
        )
        
        # Convert to traits data
        traits_data = self.trait_handler.asset_to_traits_data(asset, ["relationshipManagement"])
        
        # Check relationship trait structure
        self.assertIn("relationshipManagement", traits_data)
        relationships = traits_data["relationshipManagement"]["relationships"]
        self.assertEqual(len(relationships), 2)
        
        # Check first relationship
        self.assertEqual(relationships[0]["targetId"], "dep1")
        self.assertEqual(relationships[0]["type"], "reference")
        self.assertEqual(relationships[0]["optional"], False)
        self.assertEqual(relationships[0]["metadata"]["purpose"], "texture")
        
        # Check second relationship
        self.assertEqual(relationships[1]["targetId"], "dep2")
        self.assertEqual(relationships[1]["type"], "requires")
        self.assertEqual(relationships[1]["optional"], True)
        self.assertEqual(relationships[1]["metadata"]["purpose"], "model")
        
    def test_validate_traits_data(self):
        """Test validation of traits data against required traits."""
        # Create traits data
        traits_data = {
            "defaultName": {"name": "Test Asset"},
            "locatableContent": {"location": "/path/to/asset"},
            "versionedContent": {"version": 1}
        }
        
        # Validate against required traits
        success, missing = self.trait_handler.validate_traits_data(
            traits_data, ["basic", "versionedContent"])
        
        # Should succeed with no missing traits
        self.assertTrue(success)
        self.assertEqual(missing, [])
        
        # Validate against additional required traits
        success, missing = self.trait_handler.validate_traits_data(
            traits_data, ["basic", "versionedContent", "mediaSource"])
        
        # Should fail with mediaSource missing
        self.assertFalse(success)
        self.assertEqual(missing, ["mediaSource"])


if __name__ == "__main__":
    unittest.main()
