import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

Flickable {
    id: root
    default property alias content: contentLayout.data
    property alias spacing: contentLayout.spacing
    property int contentMinimumWidth: 0
    property int margins: 10
    property int focusMargin: 18
    property int focusBottomMargin: 10
    property int overlayBottomMargin: 0
    property var containingWindow: Window.window
    property bool scrollbarVisible: moving || dragging || hideScrollbarTimer.running || verticalScrollBar.pressed || verticalScrollBar.hovered

    clip: true
    interactive: true
    boundsBehavior: Flickable.StopAtBounds
    flickableDirection: Flickable.HorizontalAndVerticalFlick
    contentWidth: contentLayout.width + margins * 2
    contentHeight: contentLayout.implicitHeight + margins * 2 + focusBottomMargin + overlayBottomMargin

    onHeightChanged: scheduleEnsureActiveFocusVisible()
    onVisibleChanged: scheduleEnsureActiveFocusVisible()
    onContentHeightChanged: scheduleEnsureActiveFocusVisible()
    onContentYChanged: showScrollbarTemporarily()
    onMovementStarted: showScrollbarTemporarily()
    onMovementEnded: hideScrollbarTimer.restart()

    function scheduleEnsureActiveFocusVisible() {
        focusEnsureTimer.restart()
    }

    function showScrollbarTemporarily() {
        if (root.contentHeight <= root.height) {
            return
        }
        hideScrollbarTimer.restart()
    }

    function containsItem(item) {
        var current = item
        while (current) {
            if (current === root || current === root.contentItem || current === contentLayout) {
                return true
            }
            current = current.parent
        }
        return false
    }

    function clamp(value, minimum, maximum) {
        return Math.max(minimum, Math.min(maximum, value))
    }

    function ensureActiveFocusVisible() {
        if (!root.visible || root.height <= 0 || !root.containingWindow) {
            return
        }

        var item = root.containingWindow.activeFocusItem
        if (!item || !containsItem(item)) {
            return
        }

        ensureItemAreaVisible(item, root.focusBottomMargin)
    }

    function ensureItemAreaVisible(item, bottomExtra) {
        if (!root.visible || root.height <= 0 || !item || !containsItem(item)) {
            return
        }

        var topLeft = item.mapToItem(root.contentItem, 0, 0)
        var bottomRight = item.mapToItem(root.contentItem, item.width, item.height)
        var itemLeft = Math.min(topLeft.x, bottomRight.x) - root.focusMargin
        var itemRight = Math.max(topLeft.x, bottomRight.x) + root.focusMargin
        var itemTop = Math.min(topLeft.y, bottomRight.y) - root.focusMargin
        var itemBottom = Math.max(topLeft.y, bottomRight.y) + Math.max(0, bottomExtra)
        var maxX = Math.max(0, root.contentWidth - root.width)
        var maxY = Math.max(0, root.contentHeight - root.height)

        if (itemLeft < root.contentX) {
            root.contentX = clamp(itemLeft, 0, maxX)
        } else if (itemRight > root.contentX + root.width) {
            root.contentX = clamp(itemRight - root.width, 0, maxX)
        }

        if (itemTop < root.contentY) {
            root.contentY = clamp(itemTop, 0, maxY)
        } else if (itemBottom > root.contentY + root.height) {
            root.contentY = clamp(itemBottom - root.height, 0, maxY)
        }
    }

    Timer {
        id: focusEnsureTimer
        interval: 1
        repeat: false
        onTriggered: root.ensureActiveFocusVisible()
    }

    Timer {
        id: hideScrollbarTimer
        interval: 900
        repeat: false
    }

    Connections {
        target: root.containingWindow
        function onActiveFocusItemChanged() {
            root.scheduleEnsureActiveFocusVisible()
        }
    }

    ScrollBar.vertical: ScrollBar {
        id: verticalScrollBar
        policy: ScrollBar.AsNeeded
        width: 25
        implicitWidth: 25
        implicitHeight: 50
        padding: 2
        opacity: root.scrollbarVisible ? 1 : 0

        Behavior on opacity {
            NumberAnimation {
                duration: 180
            }
        }

        contentItem: Rectangle {
            width: 15
            radius: 9
            color: parent.pressed ? "#2081ef" : "#2B3A52"
        }
        background: Rectangle {
            width: 20
            color: "#101923"
            radius: 9
        }
    }

    ColumnLayout {
        id: contentLayout
        x: root.margins
        y: root.margins
        width: Math.max(root.width - root.margins * 2, root.contentMinimumWidth)
        spacing: 16
    }
}
