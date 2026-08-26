package net.apperdashery.demo.ai_rag_android

import android.app.Activity
import android.app.Application
import net.apperdashery.demo.ai_rag_android.store.AppStore

class OshaApplication : Application() {
    val appStore by lazy { AppStore() }
}

val Activity.appStore: AppStore
    get() = (application as OshaApplication).appStore
