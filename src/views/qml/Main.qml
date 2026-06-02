import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15
import "pages"

ApplicationWindow {
    id: window
    width: 1024
    height: 768
    minimumWidth: 1024
    minimumHeight: 768
    maximumWidth: 1024
    maximumHeight: 768
    visibility: Window.FullScreen
    visible: true
    title: mainViewModel.app_title
    color: "#0d141d"
    font.family: "Roboto"

    PrinterPage {
        anchors.fill: parent
        viewModel: mainViewModel
    }
}
