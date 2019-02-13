# Rejoiner Python Exercise

## Introduction

In this task, you will work with a very basic e-commerce data tracking mechanism.
The application will simply collect data about items which the customer adds
to their cart.

You may assume that there is some mechanism on the e-commerce website which
makes requests to your tracker application according to the specification listed
below.

## Background

You have been provided with a fresh installation of a Django 2.1 project. A single
app has been added to the project called `tracker`. The goal for this task is to
write a view which accepts a request from the e-commerce website with some
data about a cart item which has been added to a specified cart ID.

This end result after receiving this request should ensure that a cart with the
specified ID exists and that it includes an item with the specified data.

## Data Model

The data model has been greatly simplified for this task and contains two tables:

- `Cart` - An object which represents a customer's online cart which can contain
several items.
- `Item` - An object which represents a single item in the cart.

These models are defined in `tracker/models.py`

## Endpoint Specification

```
POST /items
```

This endpoint adds an item to the current cart using the following logic:

- The current cart ID will be the first valid UUID found in one of the
following sources, in order of priority:
    1. The `cart_id` cookie sent with the request
    1. The `cart_id` parameter in the body of the request
    1. If neither exists nor is valid, a new cart ID should be generated.

### JSON Payload

Name | Type | Description | Required
-- | -- | -- | --
`product_id` | String | ID which represents the product on the e-commerce site. (e.g. a SKU) | Yes
`cart_id` | String | ID of the current cart stored in the first-party cookie. | No
`name` | String | The name of the product. | No
`price` | Integer | The price of the item (in cents). | No

### Cookies

The following third-party cookies may be included with the request.

Name | Type | Description | Required
-- | -- | -- | --
`cart_id` | String | ID of the current cart. | No

### Response

The endpoint returns the ID of the current cart as a JSON payload. The e-commerce website
will then store the result of this response as a first-party cookie for future requests.

Name | Type | Description | Required
-- | -- | -- | --
`cart_id` | String | ID of the current cart. | Yes

The response should also store the `cart_id` in a cookie on its own domain in the response.

## Performance

The tracker is expected to receive large amounts of data from many clients, so
the time it takes for the request to be processed and generate a response is critical.

One of the primary rating criteria is implementing the tracker endpoint with this
requirement in mind.

**Tip:** Consider the actual requirements in order to render the response. The primary
keys are not sequential for a reason.

## Guidelines

- Follow best Python standards and practices (i.e. PEP8)
- Implement unit tests for your code. Integration tests may also be useful for
writing your application.
- Include any documentation on how to run your app and be sure to update the
`requirements.txt` file if necessary.
- Feel free to utilize any other libraries (e.g. Django Rest Framework) or services
(e.g. redis) that you feel may be of use in completing the task.
