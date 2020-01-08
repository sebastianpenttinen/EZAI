doc_template = '''
## Iris species classification 

### Overview
This is a model for classifying iris flowers based on the observed flowers petal length, petal width, sepal length, sepal width. The model predicts the species of iris flowers. 

### Usage 
The model parameters are taken as a feature vector in the following manner.

```javascript
fetch(“ai.com/api/”, {
	method: “post”
	headers: {
        	“Accept”: “application/json”,
	        “Content-Type”: “application/json”
	},

	body: JSON.Stringify({
		model_params: [[1,2,3,4]]    // parameters to predict 
	})
})
.then((response) => {
    // Check if response valid 

    // Use prediction 
})
```

### Data
The iris dataset consists of 150 rows of flowers, with 5 features - Petal Length, Petal Width, Sepal Length, Sepal width and Class(Species). 

More information on the dataset can be found from: https://www.kaggle.com/arshid/iris-flower-dataset
'''