from tkinter import simpledialog, messagebox, PhotoImage
from enum import Enum
from mainframe import MainFrame, ToolAction
from noteeditor import NoteEditor
from notestree import NotesTree, TreeAction, TreeItem
from folderdialog import FolderDialog
from note import Note
from business import BusinessLogic
from libs import *
from globals import FOLDER, NOTE
from images import ImageFactory #imgFolder, imgNote

class SaveResult( Enum ):
    OK = 1,
    NEED_CAPTION = 2,
    NEED_FOLDER = 3,
    CANCEL = 4

class Controller:
    def __init__( self, mainframe:MainFrame ):
        self._mainframe = mainframe
        self._tree:NotesTree = mainframe.tree
        self._edi:NoteEditor = mainframe.edi
        self._edi.setCtrlSCallback( self.onCtrlS )
        self._status = mainframe.statusbar
        self._tree.setTreeCallback( self._treeCallback )
        self._mainframe.setToolActionCallback( self.toolActionCallback )
        self._folder_id_iid_ref:Dict = { 0: '' }  #key: id, value: iid
        self._note_id_iid_ref:Dict = {} #key: id, value: iid
        self._imgFolder:PhotoImage #= PhotoImage( file="/home/martin/Projects/python/notes/images/folder_16.png" )
        self._imgNote:PhotoImage #= PhotoImage( file="/home/martin/Projects/python/notes/images/note_16.png" )
        self._business = BusinessLogic()

    def startWork( self ):
        self._imgFolder = ImageFactory.getInstance().imgFolder
        self._imgNote = ImageFactory.getInstance().imgNote
        # set tree's folders:
        self._setFolders( parent_id = 0, parent_iid = '' )
        self._setNotes()

    def _setFolders( self, parent_id:int, parent_iid:str ):
        folders: List[Tuple] = self._business.getFolders( parent_id )
        for f in folders:
            id, parent_id, text = f
            iid = self._tree.addFolder( parent_iid, id, text, self._imgFolder )
            self._folder_id_iid_ref[id] = iid
            # each id could have subfolders:
            self._setFolders( id, iid )

    def _setNotes( self ):
        headers = self._business.getHeaders()
        for h in headers:
            id, parent_id, header = h
            iid_parent = self._folder_id_iid_ref[parent_id]
            self._note_id_iid_ref[id] = self._tree.addNote( iid_parent, id, header, self._imgNote )

    def _treeCallback( self, action:TreeAction, treeItems:List[TreeItem]  ) -> None:
        # itemspec: FOLDER or NOTE
        nItems:int = len( treeItems )
        if action == TreeAction.DELETE:
            if nItems == 1:
                self.deleteItem( treeItems[0] )
            else:
                self.deleteItems( treeItems )
        elif action == TreeAction.SELECT:
            treeItem = treeItems[0]
            if nItems > 1 or treeItem.isNote == False:
                return
            self._handleOneNoteSelection( treeItem )
        elif action == TreeAction.MOVE:
           self._moveAction( treeItems[0] )
        elif action == TreeAction.INSERT:
            self.newFolderAction( treeItems[0] )

    def _handleOneNoteSelection( self, treeItem:TreeItem ) -> None:
        #before changing the displayed note, check if there are unsaved changes:
        if self._edi.isModified():
            note:Note = self._edi.getNote()
            if messagebox.askyesno( "Unsaved Changes", "Note '" + note.header + "' has been modified.\nSave changes?" ):
                self.saveNoteLocalAction()

        #show selected note:
        note: Note = self._business.getNote( treeItem.id )
        self._edi.setNote( note )

    def _moveAction( self, treeItem:TreeItem ):
        def _onOk( ok:bool ):
            folder:TreeItem = folderDlg.getSelectedFolder()
            if treeItem.isNote:
                self._business.changeNoteParent( treeItem.id, folder.id )
                self._tree.moveItem( treeItem.iid, folder.iid )
            else:
                self._business.changeFolderParent( treeItem.id, folder.id )
                self._tree.moveItem( treeItem.iid, folder.iid )

        folderDlg = FolderDialog( self._mainframe )
        folderDlg.setOkCancelCallback( _onOk )

    def _syncIdIIdReferences( self ):
        #note id/iid references:
        idlist:List[int] = self._business.getAllNoteIds()
        self._note_id_iid_ref = [x for x in self._note_id_iid_ref if x in set( idlist )]
        #folder id/iid references:
        idlist = self._business.getAllFolderIds()
        self._folder_id_iid_ref = [x for x in self._folder_id_iid_ref if x in set( idlist )]

    def deleteItems( self, treeItems:List[TreeItem] ):
        yes = messagebox.askyesno( "Confirmation Prompt", "Really delete the selected items?", icon='warning' )
        if not yes: return

        for item in treeItems:
            self.deleteItem( item, False )

    def deleteItem( self, treeItem:TreeItem, ask:bool = True ):
        yes:bool = True
        if ask:
            q =  "Really delete this folder and all its content?" if treeItem.isNote == False else \
                "Really delete this note?"
            yes = messagebox.askyesno( "Confirmation Prompt", q, icon='warning' )
        if yes:
            self._business.deleteItem( treeItem.id, NOTE if treeItem.isNote else FOLDER )
            self._tree.remove( treeItem.iid )
            if treeItem.isNote:
                self._note_id_iid_ref.pop( treeItem.id )
            else:
                #The deleted folder might have contained subfolders and notes.
                #We have to synchronize _folder_id_iid_ref and _note_id_iid_ref.
                self._syncIdIIdReferences()

    def toolActionCallback( self, action:ToolAction ) -> None:
        if action == ToolAction.NEW_TOPFOLDER:
            self.newTopFolderAction()
        if action == ToolAction.NEW_NOTE:
            #print( "Controller.toolActionCallback - ToolAction.NEW_NOTE" )
            self.newNoteAction()
        if action == ToolAction.SAVE_LOCAL:
            self.saveNoteLocalAction()

    def onCtrlS( self ):
        self.saveNoteLocalAction()

    def newTopFolderAction( self ):
        s = simpledialog.askstring( "New top level folder", "Name of new folder:", initialvalue="" )
        if s:
            id:int = self._business.createTopLevelFolder( s )
            self._tree.addFolder( '', id, s, self._imgFolder, True )

    def newFolderAction( self, treeItem:TreeItem ):
        s = simpledialog.askstring( "New folder", "Name of new folder:", initialvalue="" )
        if s:
            id: int = self._business.createFolder( s, treeItem.id, True )
            self._tree.addFolder( treeItem.iid, id, s, self._imgFolder, True )

    def newNoteAction( self ):
        note:Note = self._edi.getNote()
        if self._edi.isModified():
            if messagebox.askyesno( "Unsaved Changes", "There are unsaved changes. Do you want them to be saved?" ):
                if self.saveNoteLocalAction() != SaveResult.OK: return
            
        self._edi.setNote( Note() )
        #print( "Controller._tree.unsetSelection" )
        self._tree.unsetSelection()

    def saveNoteLocalAction( self ) -> SaveResult:
        """
        First check if this is the first time the note is saved.
        If so, check if a folder is selected. If not, give a proper hint.
        Save the note
        """
        note:Note = self._edi.getNote()
        if len( note.header ) == 0:
            if not messagebox.askyesno( "No Heading specified", "Do you really wish to save this note without caption?\n"
                                                                "No text will be shown in the tree afterwards." ):
                return SaveResult.NEED_CAPTION
            
        if note.id <= 0:
            #new note, not yet saved
            iid_parent = ''
            iid, id, text, itemspec = self._tree.getSelectedTreeItemAsTuple()
            if iid == '0' or iid == '':
                # no tree item selected
                if not messagebox.askyesno( "No Folder Selected", "Do you really wish to save this note outside any folder?" ):
                    return SaveResult.NEED_FOLDER
            else: # a tree item is selected - is it a note or a folder?
                if not itemspec == FOLDER:
                    # another note is selected (and opened). Get that note's folder.
                    folder_id, foldername = self._business.getNoteFolder( id )
                    iid_parent = self._folder_id_iid_ref[folder_id]
                    note.parent_id = folder_id
                else:
                    # a folder is selected. Make sure the new note is to be saved in this folder.
                    iid_parent = iid
                    note.parent_id = id
                    foldername = text

                if not messagebox.askyesno( "Save Note", "Save this note in folder\n" + foldername + "?" ):
                    return SaveResult.CANCEL

            self._business.insertNote( note )
            self._tree.addNote( iid_parent, note.id, note.header, self._imgNote )
            return SaveResult.OK
        else:
            #update an existing note
            self._business.updateNote( note )
            self._edi.resetModified()
            #maybe the header has changed, so let the tree update its label
            item_iid = self._note_id_iid_ref[note.id]
            self._tree.updateLabel( item_iid, note.header )
            return SaveResult.OK