# FabricRestTool

## High level description
FabricRestTool is a desktop application, which allows for creating interactive automatizations taking advantage of the Microsoft Fabric Rest API endpoints.

## Main requirements
* The application should provide the user the invocation of the Fabric and Power BI REST API endpoints
* The authentication should be able to handle MFA user authentication as well as Service Principal authentication for technical users
* The application have to be able to describe complex automatizations, which are running in the name of the authenticated account
* The appliaction should be easy to extend with new endpoints in the future
* The application should be efficient, e.g. metadata querying it should minimize the amount of REST request



## User interface
The application should follow a borwser-like tab based structure, where there are multiple tabs, but only one is currently active.

Use the 

The user interface should consist of 3 main segments.
1. On the top part of the page there should be a bar, which is devided into 3 further segments
    1. On the left side a plus which opens a function into a new tab
    1. On the middle the list of tabs, from which the current one is highlighted
    1. On the right side, the current user and the settings options are visible
1. The main screen where the currently active tab's details and contents is visible
1. On the left side the collection of possible actions and functions related to the active tab's feature

Design:
* Use animations if possible, but avoid large overhead or complicated ones
* Use dark theme


## Features
The currently active tab's feature can be one of the followings:
* Call specific endpoint
* Define pipeline
* Generate code


### Invoke specific endpoint

The application should enable the user to invoke all Fabric or Power BI endpoint, to let him/her test it's capabilities.

**Funcitonalities**
* The possible values for the required and optoinal parameters for the specific request should be selected from a dropdown window in case of predefined parameters
* The values of the dropdown window should be user friendly, avoid showing IDs, show the associated item's name alongside it's ID, e.g. defining the workspaceId should be selected from all the available workspaces to the authenticated user and represented by the names of the workspace alongside with it's GUID
* There should be a searchbar which allows for browsing for a specific endpoint
* The response of the endpoint should be presented without any special transofrmation (pretty print or syntax highlight is allowed) 


### Define Pipeline

The application should allow for defining pipelines.
A pipeline is defined by items. The list of the possible items are:
* REST API endpoint invoke
* Loops
* Conditions (if-else)
* Variables
* Parameters

**Features**
* The items of a pipeline can be placed in any order into a pipeline
* Items can be connected, which determines a dependency between the two items
* Based on the type of the connection the dependent object should be executed after the referenced item finishes based on it's result
* The connections can have multiple types which determines, in case of which result should the dependent item start
* The dependency types are:
    * Success -> The dependent object only starts when all the referenced items finished with success
    * Failure -> The dependent object only starts when all the referenced items finished with failure
    * Finished -> The dependent object only starts when all the referenced items finished, this case the result does not matter
* The items of the pipelines should be configurable, they can reference:
    * Parameters
    * Variables
    * Results of other items
    * Parts of results of other items
* If there is no direct or indirect releationship between two items their execution order is not defined and is sorted by their name alphabetically
* A pipeline have to be able to be saved in a descriptor
* Pipelines can be imported from descriptors
* Pipelines can be edited freely, but before exporting a validation should check for incosistencies and ask the user to resolve those, the validatoin should include:
    * One item cannot depend by itself
    * Multiple items can reference the same item
    * One item can reference multiple other items
    * There cannot be cycles in the dependency graph
    * There can only be one direct dependency defined between two items

### Code Generation

The application should be able to materialize the pipelines into codes executable scripts.

**Features**
* The pipelines should be materialized deterministicly according to their descriptor
* The pipelines should be generated in python
* The executionorder of independent parts of the pipeline have to be defined by the user
    * in case of parallel execution, execute the unrelated parts from the same threadpool
    * in case of linear, execute the unrelated parts by the first alphabetically based on the first item's name in each part
* Materialized pipelines can be imported to descriptors

## Make sure to
* In case of inconsistency stop, suggest a solution, but do not progress by yourself
* In case of poor definition stop, suggest solution, but do not progress by yourself
