### Running Lint Rules
You may also want to run some rules against your repository to see all current violations.

- To run only the pre-packaged Fixit rules against the entire repository, run:
    ```bash
    python -m fixit.cli.run_rules --rules fixit.rules
    ```

- To run only your custom rules package against the entire repository, run:
    ```bash
    python -m fixit.cli.run_rules --rules <dotted_name_of_custom_package>
    ```

- To run a specific rule against the entire repository, run:
    ```bash
    python -m fixit.cli.run_rules --rules <rule_name>
    ```

- To run all the rule packages under the packages settings in the .fixit.config.yaml file against the entire repository, run:
    ```bash
    python -m fixit.cli.run_rules
    ```

- To run all the rule packages under the packages settings in the .fixit.config.yaml file against a particular file or directory, run:
    ```bash
    python -m fixit.cli.run_rules <file_or_directory>
    ```

- To run all the rule packages under the packages settings in the .fixit.config.yaml file against mutliple files or directories, run:
    ```bash
    python -m fixit.cli.run_rules <file_or_directory> <file_or_directory2> <file_or_directory3>
    ```

### Applying Autofixes

Some rules come with provided autofix suggestions. 
We have provided a script to help you automatically apply these suggested fixes. To do this, run:

```bash
python -m fixit.cli.apply_fix <file_or_directory> --rules <rule_name_or_package>
```

### Running Test
```bash
python -m unittest tests 
```