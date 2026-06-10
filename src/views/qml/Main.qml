import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15
import "pages"

ApplicationWindow {
    id: window
    width: Screen.width 
    height: Screen.height
    minimumWidth: 1200
    minimumHeight: 800
    visibility: Window.Maximized
    flags: Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowTitleHint
    visible: true
    title: mainViewModel.app_title
    color: "#0d141d"
    font.family: "Roboto"

    PrinterPage {
        anchors.fill: parent
        viewModel: mainViewModel
    }
}
