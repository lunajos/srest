import pytest
from src.parsers.submit import SlurmDirectiveParser, OutputFormat

def test_parse_empty_script():
    """Test parsing empty script"""
    script = ""
    content, params = SlurmDirectiveParser.parse_script(script)
    assert content == ""
    assert params == {}

def test_parse_script_no_directives():
    """Test parsing script without directives"""
    script = "echo test"
    content, params = SlurmDirectiveParser.parse_script(script)
    assert content == "echo test"
    assert params == {}

def test_parse_script_with_directives():
    """Test parsing script with directives"""
    script = """#!/bin/bash
#SBATCH --job-name=test
#SBATCH --partition=debug
#SBATCH --time=1:00:00
#SBATCH --mem=4G
#SBATCH --array=1-10:2

echo test"""
    content, params = SlurmDirectiveParser.parse_script(script)
    assert content == "#!/bin/bash\n\necho test"
    assert params['job_name'] == 'test'
    assert params['partition'] == 'debug'
    assert params['time'] == '1:00:00'
    assert params['mem'] == '4G'
    assert params['array'] == '1-10:2'

def test_parse_script_with_comments():
    """Test parsing script with regular comments"""
    script = """#!/bin/bash
# Regular comment
#SBATCH --job-name=test
# Another comment
echo test"""
    content, params = SlurmDirectiveParser.parse_script(script)
    assert '# Regular comment' in content
    assert '# Another comment' in content
    assert params['job_name'] == 'test'

def test_parse_memory():
    """Test memory parsing"""
    test_cases = [
        ('1K', 1),
        ('1M', 1024),
        ('1G', 1024*1024),
        ('1T', 1024*1024*1024),
        ('1.5G', int(1.5*1024*1024)),
    ]
    for input_str, expected_mb in test_cases:
        assert SlurmDirectiveParser.parse_memory(input_str) == expected_mb

def test_parse_time():
    """Test time parsing"""
    test_cases = [
        ('1', 1),
        ('1:30', 90),
        ('1:30:00', 90),
        ('1-00:00:00', 24*60),
        ('2-12:00:00', 60*60),
    ]
    for input_str, expected_minutes in test_cases:
        assert SlurmDirectiveParser.parse_time(input_str) == expected_minutes

def test_invalid_memory():
    """Test invalid memory format"""
    with pytest.raises(ValueError):
        SlurmDirectiveParser.parse_memory('invalid')

def test_invalid_time():
    """Test invalid time format"""
    with pytest.raises(ValueError):
        SlurmDirectiveParser.parse_time('invalid')

def test_output_format():
    """Test output format enum"""
    assert OutputFormat.BASIC.value == 'basic'
    assert OutputFormat.JSON.value == 'json'
    assert OutputFormat.DETAILED.value == 'detailed'
    assert OutputFormat.PARSABLE.value == 'parsable'