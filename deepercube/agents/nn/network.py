import torch
from deepercube.utils import wrappers
from deepercube.agents.nn.noisy_linear import NoisyLinear

# from deepercube.agents.nn.noisy_linear_torchrl import NoisyLinear


class OneHot(torch.nn.Module):
    def __init__(self, num_classes: int) -> None:
        super().__init__()
        self.num_classes = num_classes

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        oh = torch.nn.functional.one_hot(x, self.num_classes)
        return oh.reshape(x.shape[0], -1).type(torch.float32)


class Identity(torch.nn.Module):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x


class DeepCubeACore(torch.nn.Module):
    """
    DeepCubeA network architecture without the output layer.

    Agostinelli, F., McAleer, S., Shmakov, A., & Baldi, P. (2019). Solving the Rubik’s cube with deep reinforcement learning and search. Nature Machine Intelligence, 1(8), 356–363.

    Params:
        `in_features`: number of input features
        `noisy`: if True, NoisyLinear layers will be used instad of Linear
        `norm`:
            - None: no normalization
            - "layer": LayerNorm
            - "batch": BatchNorm
    Returns:
        DeepCubeA with `in_features` inputs and 1000 outputs.
        User should add custom last layer on top of this core model.

    Examples:
        ```python
        model = torch.nn.Sequential(
            OneHot(6),
            DeepCubeACore(6*54, noisy=False),
            torch.nn.Linear(1000, 6)
        )
        ```
    """

    def __init__(self, in_features: int, noisy: bool = False, norm: str|None = None) -> None:

        def res_block():
            nonlocal Linear
            nonlocal Norm
            return torch.nn.Sequential(
                Linear(1000, 1000, bias=False),
                Norm(1000),
                torch.nn.ReLU(),
                Linear(1000, 1000),
                Norm(1000),
            )

        super().__init__()
        Linear = NoisyLinear if noisy else torch.nn.Linear

        Norm = Identity
        if norm is not None:
            if norm == "layer":
                Norm = torch.nn.LayerNorm
            elif norm == "barch":
                torch.nn.BatchNorm1d
            else:
                assert False, "Unknown type of normalization!"

        self.relu = torch.nn.ReLU()

        self.l1 = Linear(in_features, 5000, bias=False)
        self.bn1 = Norm(5000)

        self.l2 = Linear(5000, 1000, bias=False)
        self.bn2 = Norm(1000)

        self.res_blocks = torch.nn.ParameterList([res_block() for _ in range(4)])

        if not noisy:
            self.apply(wrappers.torch_init_with_xavier_and_zeros)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        hidden = self.l1(x)
        hidden = self.bn1(hidden)
        hidden = self.relu(hidden)

        hidden = self.l2(hidden)
        hidden = self.bn2(hidden)
        hidden = self.relu(hidden)

        for res_block in self.res_blocks:
            skip = hidden
            res = res_block(hidden)
            hidden = res + skip
            hidden = self.relu(hidden)

        return hidden
