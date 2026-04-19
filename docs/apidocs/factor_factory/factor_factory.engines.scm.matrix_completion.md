# {py:mod}`factor_factory.engines.scm.matrix_completion`

```{py:module} factor_factory.engines.scm.matrix_completion
```

```{autodoc2-docstring} factor_factory.engines.scm.matrix_completion
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`MatrixCompletionEngine <factor_factory.engines.scm.matrix_completion.MatrixCompletionEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.scm.matrix_completion.MatrixCompletionEngine
    :summary:
    ```
````

### API

`````{py:class} MatrixCompletionEngine
:canonical: factor_factory.engines.scm.matrix_completion.MatrixCompletionEngine

```{autodoc2-docstring} factor_factory.engines.scm.matrix_completion.MatrixCompletionEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.scm.matrix_completion.MatrixCompletionEngine.name
:value: >
   'matrix_completion'

```{autodoc2-docstring} factor_factory.engines.scm.matrix_completion.MatrixCompletionEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, treatment: str = 'treatment', rank_penalty: float = 1.0, max_iter: int = 500, tol: float = 1e-05, **_engine_specific_kwargs: typing.Any) -> factor_factory.engines.scm._base.ScmResult
:canonical: factor_factory.engines.scm.matrix_completion.MatrixCompletionEngine.fit

```{autodoc2-docstring} factor_factory.engines.scm.matrix_completion.MatrixCompletionEngine.fit
```

````

`````
