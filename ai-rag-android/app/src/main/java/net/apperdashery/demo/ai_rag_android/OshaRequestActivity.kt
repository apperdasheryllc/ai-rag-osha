package net.apperdashery.demo.ai_rag_android

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import net.apperdashery.demo.ai_rag_android.store.AppAction
import net.apperdashery.demo.ai_rag_android.store.AppStore
import net.apperdashery.demo.ai_rag_android.store.OshaAction
import net.apperdashery.demo.ai_rag_android.store.OshaRoute
import net.apperdashery.demo.ai_rag_android.ui.theme.AiragandroidTheme

class OshaRequestActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            AiragandroidTheme {
                OshaRequestScreen(
                    store = appStore,
                    onNavigateToResponse = {
                        startActivity(Intent(this, OshaResponseActivity::class.java))
                    }
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun OshaRequestScreen(store: AppStore, onNavigateToResponse: () -> Unit) {
    val state by store.state.collectAsStateWithLifecycle()
    var query by remember { mutableStateOf("") }

    LaunchedEffect(state.osha.route) {
        if (state.osha.route == OshaRoute.Response) {
            onNavigateToResponse()
            store.dispatch(AppAction.Osha(OshaAction.NavigationHandled))
        }
    }

    Scaffold(
        topBar = { TopAppBar(title = { Text("OSHA PPE Assistant") }) }
    ) { innerPadding ->
        Box(modifier = Modifier.fillMaxSize().padding(innerPadding)) {
            Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
                Text("Ask about OSHA PPE regulations")
                OutlinedTextField(
                    value = query,
                    onValueChange = { query = it },
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 8.dp),
                    minLines = 5
                )
                Button(
                    onClick = {
                        store.dispatch(AppAction.Osha(OshaAction.AskExpertTapped(query.trim())))
                    },
                    enabled = query.isNotBlank() && !state.osha.isLoading,
                    modifier = Modifier.padding(top = 16.dp)
                ) {
                    Text("Ask The Expert")
                }
            }

            if (state.osha.isLoading) {
                CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
            }
        }
    }
}
