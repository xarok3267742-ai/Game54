package ru.poryadok5.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import ru.poryadok5.app.data.TaskRepository
import ru.poryadok5.app.data.UserPreferencesRepository
import ru.poryadok5.app.domain.AppPreferences
import ru.poryadok5.app.domain.MicroTask
import ru.poryadok5.app.ui.PoryadokApp
import ru.poryadok5.app.ui.components.AppCard
import ru.poryadok5.app.ui.components.LoadingState
import ru.poryadok5.app.ui.components.PrimaryAction
import ru.poryadok5.app.ui.theme.PoryadokTheme
import ru.poryadok5.app.ui.theme.SageSoft
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            PoryadokTheme {
                val appContext = applicationContext
                val taskRepository = remember { TaskRepository(appContext) }
                val preferencesRepository = remember { UserPreferencesRepository(appContext) }
                val preferences: AppPreferences? by preferencesRepository.preferences.collectAsStateWithLifecycle(
                    initialValue = null,
                )

                var tasks by remember { mutableStateOf<List<MicroTask>?>(null) }
                var loadError by remember { mutableStateOf<String?>(null) }
                var loadAttempt by remember { mutableIntStateOf(0) }

                LaunchedEffect(taskRepository, loadAttempt) {
                    tasks = null
                    loadError = null
                    runCatching {
                        withContext(Dispatchers.IO) { taskRepository.loadTasks() }
                    }.onSuccess {
                        tasks = it
                    }.onFailure {
                        loadError = "Не удалось прочитать локальный список задач."
                    }
                }

                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background,
                ) {
                    when {
                        loadError != null -> StartupErrorState(
                            message = loadError.orEmpty(),
                            onRetry = { loadAttempt += 1 },
                        )
                        tasks == null -> LoadingState("Готовим задачи")
                        preferences == null -> LoadingState("Загружаем прогресс")
                        else -> PoryadokApp(
                            tasks = tasks.orEmpty(),
                            preferences = preferences ?: AppPreferences(),
                            preferencesRepository = preferencesRepository,
                        )
                    }
                }
            }
        }
    }
}

@androidx.compose.runtime.Composable
private fun StartupErrorState(message: String, onRetry: () -> Unit) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center,
    ) {
        Column(
            modifier = Modifier
                .widthIn(max = 520.dp)
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            AppCard(containerColor = SageSoft) {
                Text(
                    text = "Не удалось запустить приложение",
                    style = MaterialTheme.typography.titleLarge,
                )
                Text(
                    text = message,
                    style = MaterialTheme.typography.bodyLarge,
                )
                Text(
                    text = "Каталог хранится на устройстве. Попробуйте загрузить его ещё раз.",
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
            PrimaryAction("Повторить загрузку", onRetry)
        }
    }
}
