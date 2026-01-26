
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    // Đăng ký chat participant
    const participant = vscode.chat.createChatParticipant('myExtension.myAgent', async (request, context, response, token) => {
        // Xử lý câu hỏi từ user
        const userQuery = request.prompt;
        
        // Trả lời
        response.markdown(`Bạn đã hỏi: ${userQuery}`);
    });
    
    participant.iconPath = vscode.Uri.joinPath(context.extensionUri, 'icon.png');
    
    context.subscriptions.push(participant);
}