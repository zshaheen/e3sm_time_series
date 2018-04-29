Can we now use variables of a different shape?

How to calculate the ANN climo, given the other seasons?
- Do we just average them?

When you do:
```python
output_vars[season] += climo
output_vars[season] /= 2
```
The `id` attr of `output_vars[season]` is removed. It used to be the variable name.
However, the `id` from `climo` is the variable, so that is okay.
I guess that adding messes something up? Commenting out the division is still okay.
Why is this?


When using one or more variable, only the final variable is saved to the resultant nc file.

