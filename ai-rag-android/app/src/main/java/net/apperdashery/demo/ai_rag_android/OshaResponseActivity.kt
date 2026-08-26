package net.apperdashery.demo.ai_rag_android

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import net.apperdashery.demo.ai_rag_android.model.OshaSource
import net.apperdashery.demo.ai_rag_android.model.OshaStandardResponse
import net.apperdashery.demo.ai_rag_android.store.AppAction
import net.apperdashery.demo.ai_rag_android.store.AppStore
import net.apperdashery.demo.ai_rag_android.store.OshaAction
import net.apperdashery.demo.ai_rag_android.ui.theme.AiragandroidTheme

class OshaResponseActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            AiragandroidTheme {
                OshaResponseScreen(
                    store = appStore,
                    onDismiss = {
                        appStore.dispatch(AppAction.Osha(OshaAction.DismissedResponse))
                        finish()
                    }
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun OshaResponseScreen(store: AppStore, onDismiss: () -> Unit) {
    val state by store.state.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Expert Answer") },
                navigationIcon = {
                    IconButton(onClick = onDismiss) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        val errorMessage = state.osha.errorMessage
        val response = state.osha.response

        when {
            errorMessage != null -> ErrorContent(
                message = errorMessage,
                onRetry = onDismiss,
                modifier = Modifier.fillMaxSize().padding(innerPadding)
            )

            response != null -> AnswerContent(
                response = response,
                modifier = Modifier.fillMaxSize().padding(innerPadding)
            )

            else -> Text(
                "No response available.",
                modifier = Modifier.fillMaxSize().padding(innerPadding).padding(16.dp)
            )
        }
    }
}

@Composable
private fun ErrorContent(message: String, onRetry: () -> Unit, modifier: Modifier = Modifier) {
    Column(modifier = modifier.padding(16.dp)) {
        Text("Something went wrong", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.error)
        Text(message, modifier = Modifier.padding(top = 8.dp))
        Button(onClick = onRetry, modifier = Modifier.padding(top = 16.dp)) {
            Text("Try Again")
        }
    }
}

@Composable
private fun AnswerContent(response: OshaStandardResponse, modifier: Modifier = Modifier) {
    LazyColumn(modifier = modifier.padding(16.dp)) {
        item {
            Text(response.answer)
        }

        if (response.sources.isNotEmpty()) {
            item {
                HorizontalDivider(modifier = Modifier.padding(vertical = 16.dp))
                Text("Sources", fontWeight = FontWeight.Bold)
            }

            items(response.sources) { source ->
                SourceItem(source)
            }
        }
    }
}

@Composable
private fun SourceItem(source: OshaSource) {
    val context = LocalContext.current
    Column(modifier = Modifier.padding(vertical = 8.dp)) {
        Text(source.label, fontWeight = FontWeight.SemiBold)
        Text(source.citation, style = MaterialTheme.typography.bodySmall)
        Text(source.text, style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(top = 4.dp))
        TextButton(
            onClick = {
                context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(source.sourceUrl)))
            },
            modifier = Modifier.padding(top = 4.dp)
        ) {
            Text("View source")
        }
    }
}
