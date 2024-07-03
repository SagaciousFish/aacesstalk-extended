package com.naver.ai.aacesstalk.client

import android.os.Bundle
import android.util.Log
import android.view.KeyEvent
import com.facebook.react.ReactActivity
import com.facebook.react.ReactActivityDelegate
import com.facebook.react.defaults.DefaultNewArchitectureEntryPoint.fabricEnabled
import com.facebook.react.defaults.DefaultReactActivityDelegate
import com.globalkeyevent.GlobalKeyEventModule

class MainActivity : ReactActivity() {

    /**
     * Returns the name of the main component registered from JavaScript. This is used to schedule
     * rendering of the component.
     */
    override fun getMainComponentName(): String = "ClientRn"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(null)
    }

    /**
     * Returns the instance of the [ReactActivityDelegate]. We use [DefaultReactActivityDelegate]
     * which allows you to enable New Architecture with a single boolean flags [fabricEnabled]
     */
    override fun createReactActivityDelegate(): ReactActivityDelegate =
        DefaultReactActivityDelegate(this, mainComponentName, fabricEnabled)

    override fun dispatchKeyEvent(event: KeyEvent?): Boolean {
        Log.d("KeyEvent", "Dispatched key event - " + event?.keyCode?.toString() + ", " + event?.action)

        if(event?.action == KeyEvent.ACTION_DOWN){
            GlobalKeyEventModule.getInstance().onKeyDownEvent(event.keyCode, event)
        }else if(event?.action == KeyEvent.ACTION_UP){
            GlobalKeyEventModule.getInstance().onKeyUpEvent(event.keyCode, event)
        }
        return super.dispatchKeyEvent(event)
    }
}
