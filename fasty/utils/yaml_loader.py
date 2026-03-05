"""
YAML configuration loader for the Fasty application.

This module handles loading, parsing, and validating the application
configuration from YAML files, including Faker data generation.
"""
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar, List
from faker import Faker

from fasty.core.models import AppConfig, ModelConfig
from fasty.core.exceptions import ConfigError

T = TypeVar('T')


def generate_fake_value(generator: str, faker: Faker) -> Any:
    """Generate a fake value using Faker based on a generator name."""
    try:
        if '.' in generator:
            _, method = generator.split('.')
            if hasattr(faker, method):
                return getattr(faker, method)()
        else:
            if hasattr(faker, generator):
                return getattr(faker, generator)()
    except Exception:
        pass
    return None


def generate_fake_data(count: int, schema: Dict[str, str], locale: str) -> List[Dict[str, Any]]:
    """Generate a list of fake data records."""
    faker = Faker(locale)
    data = []
    for i in range(count):
        item = {}
        for key, generator in schema.items():
            if key != '_count':
                item[key] = generate_fake_value(generator, faker)
        item['id'] = i + 1
        data.append(item)
    return data


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """
    Load and parse a YAML file.

    Args:
        file_path: Path to the YAML file

    Returns:
        Parsed YAML content as a dictionary

    Raises:
        ConfigError: If the file cannot be read or parsed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                return yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                raise ConfigError(f"Invalid YAML in {file_path}: {str(e)}")
    except IOError as e:
        raise ConfigError(f"Could not read config file {file_path}: {str(e)}")


def validate_config(config_data: Dict[str, Any]) -> AppConfig:
    """
    Validate configuration data and generate fake data if needed.
    """
    try:
        locale = config_data.get('locale', 'en_US')
        models_raw = config_data.get('models', {})

        processed_models = {}
        for model_name, model_data in models_raw.items():
            # Generate fake data if specified
            if 'fake' in model_data and '_count' in model_data['fake']:
                count = model_data['fake']['_count']
                generated = generate_fake_data(
                    count, model_data['fake'], locale)

                # Merge with manual data if exists
                manual_data = model_data.get('data', [])
                for item in manual_data:
                    if 'id' not in item:
                        item['id'] = len(generated) + 1
                    generated.append(item)

                model_data['data'] = generated

            processed_models[model_name] = {**model_data, 'name': model_name}

        config_data['models'] = processed_models
        return AppConfig(**config_data)
    except Exception as e:
        raise ConfigError(f"Configuration validation failed: {str(e)}")


def load_and_validate_config(file_path: Path) -> AppConfig:
    """
    Load and validate a YAML configuration file.

    Args:
        file_path: Path to the YAML configuration file

    Returns:
        Validated AppConfig instance

    Raises:
        ConfigError: If loading or validation fails
    """
    if not file_path.exists():
        raise ConfigError(f"Config file not found: {file_path}")

    config_data = load_yaml_file(file_path)
    return validate_config(config_data)
