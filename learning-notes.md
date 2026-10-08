# Real-Time Attribution Dashboard — Learning Notes

## Environment Setup

### Python

Python is the programming language used for the project.

Version:

3.14.8

### Python Virtual Environment

A Python virtual environment isolates the packages required
by this project from the system-wide Python installation.

Created with:

    python -m venv .venv

Activated in PowerShell with:

    .venv\Scripts\Activate.ps1

PowerShell initially blocked the activation script because
script execution was disabled.

I changed the execution policy for my current Windows user
account to `RemoteSigned`:

    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

After activation, the terminal showed `(.venv)`.

### Environment Verification

Python version:

3.14.8

pip version:

26.2.1

The pip installation is located inside the project's `.venv`
directory, confirming that the virtual environment is active.

---

## Git Setup

The project was initialized as a Git repository with:

    git init

Git username and email were configured so commits are
associated with the project author.

---

## Next Steps

- Install required Python packages
- Set up Google Cloud
- Configure BigQuery
- Inspect the GA4 public dataset
- Create the dbt project
- Build staging models
- Build intermediate models
- Build attribution models
- Implement First-Click attribution
- Implement Last-Click attribution
- Build the streaming demonstration
- Build the Streamlit dashboard
- Add tests and documentation
- Create the architecture diagram
- Prepare the final demo