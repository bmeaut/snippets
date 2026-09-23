$base = "app"

$dirs = @(
    "$base/presentation/screens",
    "$base/presentation/viewmodel",
    "$base/presentation/state",
    "$base/presentation/navigation",

    "$base/domain/model",
    "$base/domain/usecase",
    "$base/domain/repository",
    "$base/domain/logic",

    "$base/data/local/room/dao",
    "$base/data/local/room/database",
    "$base/data/local/room/entity",

    "$base/data/remote/api",

    "$base/data/repository",
    "$base/data/mapper",

    "$base/di",

    "$base/core/util",
    "$base/core/constants",
    "$base/core/extensions"
)

$files = @(
    "$base/presentation/screens/HomeScreen.kt",
    "$base/presentation/viewmodel/HomeViewModel.kt",
    "$base/presentation/state/HomeUiState.kt",
    "$base/presentation/navigation/NavGraph.kt",

    "$base/domain/model/Food.kt",
    "$base/domain/usecase/GetFoodsUseCase.kt",
    "$base/domain/repository/FoodRepository.kt",

    "$base/data/local/room/dao/FoodDao.kt",
    "$base/data/local/room/database/KcalDatabase.kt",
    "$base/data/local/room/entity/FoodEntity.kt",

    "$base/data/remote/api/FoodApi.kt",

    "$base/data/repository/FoodRepositoryImpl.kt",

    "$base/data/mapper/FoodMapper.kt",

    "$base/di/AppModule.kt",

    "$base/core/util/Result.kt"
)

Write-Host "Creating folders..."
foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

Write-Host "Creating files..."
foreach ($file in $files) {
    New-Item -ItemType File -Force -Path $file | Out-Null
}

Write-Host "Skeleton created successfully!"