import React from 'react';
import DocumentList from './components/DocumentList';
import DocumentEditor from './components/DocumentEditor';
import DocumentHistory from './components/DocumentHistory';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';

const App = () => {
  return (
    <Router>
      <Switch>
        <Route exact path="/" component={DocumentList} />
        <Route path="/documents/:documentId" component={DocumentEditor} />
        <Route path="/documents/:documentId/history" component={DocumentHistory} />
      </Switch>
    </Router>
  );
};

export default App;