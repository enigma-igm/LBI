import jax.numpy as np
import flax.linen as nn
from typing import Sequence


class Sequential(nn.Module):
    layers: Sequence[nn.Module]

    def __call__(self, x, *args, **kwargs):
        for layer in self.layers:
            print(layer)
            if isinstance(layer, nn.Module):
                x = layer(x, *args, **kwargs)
            else:
                # activation functions don't take additional arguments
                x = layer(x)
        return x


class SeriesTransform(nn.Module):
    transformations: Sequence[nn.Module]
    context_embedding: nn.Module = None

    def __call__(self, x, context=None):
        outputs = x
        log_det_jacobian = np.zeros((x.shape[0], ))

        if self.context_embedding is not None:
            context = self.context_embedding(context)

        for transformation in self.transformations:
            outputs, log_det_J = transformation(outputs, context)
            log_det_jacobian += log_det_J
        return outputs, log_det_jacobian

    def forward(self, x, context=None):
        self(x, context)

    def inverse(self, z, context=None):
        outputs = z
        log_det_jacobian = np.zeros((z.shape[0], 1))
        for transformation in self.transformations:
            outputs, log_det_J = transformation(outputs, context)
            log_det_jacobian += log_det_J
        return outputs, log_det_jacobian
