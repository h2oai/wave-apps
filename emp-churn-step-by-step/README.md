# Step by step Apps



This is a series of self-contained Wave Apps that build upon each other. We begin with basic concepts and advance to more efficient development patterns for Wave.

The Wave App highlights the capabilities of the Wave framework. It loads prediction and Shapley values files, and presents various information about Employee Churn based on the selected employee record and probability cut-off to display Shapley values.

To install and run the code:

- Create virtual Python virtual environment - the code was tested with Python 3.8

- Install dependencies from the src/requirements.txt 

- To run wave the first App, for the conescutive Apps, replace `app1` with the `app2`, ...`app13` 

  ```bash
  wave run --no-reload src.app1
  ........................
  wave run --no-reload src.app13
  ```



Here is a list of the training Apps:

- App1 through App8: Step-by-step development of the Employee Churn dashboard
- App9: Adding debugging capabilities
- App10: Refactoring App9 to refresh content only when there is a change due to user interaction. In the previous steps, we have redrawn cards every time, even if there was no change
- App11: Same as App10 but pulling data from Delta Lake storage
- App12: App10 plus table pagination logic
- App13: App12 plus tabs and tab switching with no card recreation

To suppress Wave server messages and facilitate App debugging, define `H2O_WAVE_NO_LOG=1`.

TODO: Implement sorting and filtering logic for the Employee table. The current sorting logic applies only to the data within the current (single) page.
